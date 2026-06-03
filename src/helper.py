import json
import os
import re
import time

import fitz  # PyMuPDF
from google import genai
from google.genai import errors

from src.env import get_api_key

_client = None
MAX_RESUME_CHARS = 12_000

# Lite models first — separate free-tier quotas from gemini-2.0-flash
_DEFAULT_MODELS = (
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
)


def _get_client():
    global _client
    if _client is None:
        api_key = get_api_key("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:MAX_RESUME_CHARS]


def _parse_retry_seconds(message: str) -> float:
    match = re.search(r"retry in ([\d.]+)s", message, re.I)
    return min(float(match.group(1)) + 1 if match else 21.0, 60.0)


def _format_genai_error(exc: errors.ClientError) -> str:
    code = getattr(exc, "code", None) or "unknown"
    message = getattr(exc, "message", None) or str(exc)
    if code == 429:
        hint = (
            "Free-tier quota is used up for today. Wait ~1 minute and try again, "
            "or enable billing at https://aistudio.google.com/ and create a new API key. "
            "This app uses one API call per resume (not three) to stay within limits."
        )
    else:
        hint = (
            "Check your key at https://aistudio.google.com/apikey "
            "(prefer AIza... keys)."
        )
    return f"Gemini API error ({code}): {message}. {hint}"


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise RuntimeError("Could not parse Gemini response as JSON.")


def ask_genai(prompt, max_tokens=500):
    """Single Gemini request with retries and model fallbacks."""
    client = _get_client()
    last_error = None

    for attempt in range(3):
        for model in _DEFAULT_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "temperature": 0.4,
                        "max_output_tokens": max_tokens,
                    },
                )
                if response.text:
                    return response.text
                raise RuntimeError(f"Gemini returned an empty response (model: {model}).")
            except errors.ClientError as exc:
                last_error = exc
                code = getattr(exc, "code", None)
                err_text = str(exc).lower()

                if code == 429:
                    # Try next model; if all fail, wait and retry
                    continue
                if code == 404 or (code == 400 and "not found" in err_text):
                    continue
                raise RuntimeError(_format_genai_error(exc)) from exc

        if last_error and getattr(last_error, "code", None) == 429 and attempt < 2:
            time.sleep(_parse_retry_seconds(str(last_error)))
            continue
        break

    if last_error:
        raise RuntimeError(_format_genai_error(last_error)) from last_error
    raise RuntimeError("No Gemini model available.")


def analyze_resume(resume_text: str) -> dict:
    """
    One API call for summary, skill gaps, roadmap, and job keywords.
    Uses ~3x less quota than three separate calls.
    """
    prompt = f"""Analyze this resume and respond with ONLY valid JSON (no markdown, no extra text).
Use these exact keys:
- "summary": 2-4 sentences on skills, education, experience
- "skill_gaps": bullet-style text of missing skills, certs, experience
- "roadmap": bullet-style career improvement plan
- "job_keywords": comma-separated job titles/keywords for job search (max 8 terms)

Resume:
{resume_text}
"""
    raw = ask_genai(prompt, max_tokens=1200)
    data = _parse_json_response(raw)

    required = ("summary", "skill_gaps", "roadmap", "job_keywords")
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise RuntimeError(f"Gemini response missing fields: {', '.join(missing)}")

    return {
        "summary": str(data["summary"]).strip(),
        "skill_gaps": str(data["skill_gaps"]).strip(),
        "roadmap": str(data["roadmap"]).strip(),
        "job_keywords": str(data["job_keywords"]).strip(),
    }
