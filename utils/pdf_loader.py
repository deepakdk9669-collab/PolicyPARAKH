# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import io
from pypdf import PdfReader

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file object (Streamlit UploadedFile or file path).
    """
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
