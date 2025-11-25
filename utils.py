import os
import streamlit as st
from google import genai
import base64
import io

# Placeholder for Gemini API Key
# In Streamlit Cloud, set this in "Secrets"
API_KEY = os.environ.get("GEMINI_API_KEY", "")

@st.cache_resource
def initialize_gemini():
    """Initializes and returns the Gemini client."""
    if not API_KEY:
        st.error("🚨 Gemini API Key not found. Please set the GEMINI_API_KEY environment variable.")
        return None
    
    try:
        # Using Gemini 2.5 Flash for speed
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return None

def base64_encode_pdf(uploaded_file: io.BytesIO) -> str:
    """Reads the PDF file bytes and returns a base64 encoded string."""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
