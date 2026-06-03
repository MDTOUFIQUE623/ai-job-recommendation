import os

import fitz  # PyMuPDF
from google import genai
from google.genai import errors

from src.env import get_api_key

_client = None

# Prefer stable public model IDs (see https://ai.google.dev/gemini-api/docs/models)
_DEFAULT_MODELS = (
    os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "gemini-2.5-flash",
    "gemini-1.5-flash",
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
    """
    Extracts text from a PDF file using PyMuPDF.

    Args:
        uploaded_file: Streamlit uploaded file object.

    Returns:
        str: The extracted text from the PDF.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def _format_genai_error(exc: errors.ClientError) -> str:
    code = getattr(exc, "code", None) or "unknown"
    message = getattr(exc, "message", None) or str(exc)
    hint = (
        "Create a new key at https://aistudio.google.com/apikey "
        "(keys usually start with AIza). If you only get AQ. keys, try "
        "Google Cloud Console → APIs & Services → Credentials, or set "
        "GEMINI_MODEL=gemini-2.0-flash in Streamlit secrets."
    )
    return f"Gemini API error ({code}): {message}. {hint}"


def ask_genai(prompt, max_tokens=500):
    """
    Sends a prompt to the Google GenAI API and returns the response.

    Args:
        prompt (str): The prompt to send.
        max_tokens (int): Maximum output tokens.

    Returns:
        str: The model response text.
    """
    client = _get_client()
    last_error = None

    for model in _DEFAULT_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": 0.5,
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
            # Only try another model when this model ID does not exist
            if code == 404 or (code == 400 and "not found" in err_text):
                continue
            raise RuntimeError(_format_genai_error(exc)) from exc

    if last_error:
        raise RuntimeError(_format_genai_error(last_error)) from last_error
    raise RuntimeError("No Gemini model available.")
