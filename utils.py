import os
import streamlit as st
from google import genai
import base64
import io

@st.cache_resource
def initialize_gemini():
    """Gemini 3 Pro के लिए क्लाइंट इनिशियलाइज़ करता है।"""
    
    # 1. Streamlit Secrets से की (Key) उठाओ
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    # 2. नहीं तो Environment Variable से
    else:
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.error("🚨 API Key नहीं मिली! Settings में जाकर GEMINI_API_KEY डालें।")
        return None
    
    try:
        # लेटेस्ट google-genai SDK
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Gemini Connection Error: {e}")
        return None

def base64_encode_pdf(uploaded_file: io.BytesIO) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
