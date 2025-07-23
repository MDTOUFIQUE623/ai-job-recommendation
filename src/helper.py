import fitz #PyMuPDF
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


client = genai.Client(
    api_key=GOOGLE_API_KEY
)



def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file using PyMuPDF.
    
    Args:
        uploaded_file (str): The path to the PDF file.
    
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
    Sends a prompt to the Google-gen API and returns the response

    Args:
    prompt (str): The prompt to send to the Google-gen API
    max_tokens (int): The maximum number of tokens to generate

    Returns:
    str: The response from the Google-gen API
    
    """

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt,
        config={
            "temperature": 0.5,
            "max_output_tokens": max_tokens
        }
    )

    return response.text

