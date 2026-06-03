import fitz  # PyMuPDF
from google import genai

from src.env import get_api_key

_client = None


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


def ask_genai(prompt, max_tokens=500):
    """
    Sends a prompt to the Google GenAI API and returns the response.

    Args:
        prompt (str): The prompt to send.
        max_tokens (int): Maximum output tokens.

    Returns:
        str: The model response text.
    """
    response = _get_client().models.generate_content(
        model="gemini-2.0-flash-001",
        contents=prompt,
        config={
            "temperature": 0.5,
            "max_output_tokens": max_tokens,
        },
    )

    return response.text
