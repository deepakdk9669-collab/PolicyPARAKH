import os
import streamlit as st
from google import genai
import itertools
import base64
import io
import random

# --- SECURE KEY LOADING ---
# We fetch the list of keys from Streamlit Secrets.
# If running locally without secrets, it falls back to an empty list (and will error safely).
API_KEY_POOL = st.secrets.get("GEMINI_KEYS", [])

if not API_KEY_POOL:
    # Fallback for local testing if needed, or critical error
    st.error("🚨 Critical Security Error: No API keys found in Secrets!")
    st.stop()

# Create a cycling iterator that persists across the session
if "key_cycle" not in st.session_state:
    # Randomize start point so we don't always hammer the first key on reload
    start_index = random.randint(0, len(API_KEY_POOL) - 1)
    # Slicing trick to rotate the list start point
    rotated_pool = API_KEY_POOL[start_index:] + API_KEY_POOL[:start_index]
    st.session_state.key_cycle = itertools.cycle(rotated_pool)

@st.cache_resource
def get_next_client():
    """
    Fetches the NEXT available API key from the Secure Secrets Pool.
    """
    try:
        # Get the next key from the cycle
        current_key = next(st.session_state.key_cycle)
        
        # Initialize Gemini 3 Pro / Flash Client
        client = genai.Client(api_key=current_key)
        
        # Log masked key for debugging (safe to show in logs)
        masked_key = current_key[:4] + "...." + current_key[-4:]
        print(f"🔐 Secure Rotation: Using Key {masked_key}")
        
        return client
    except Exception as e:
        st.error(f"Rotation Error: {e}")
        return None

def initialize_gemini():
    return get_next_client()

def base64_encode_pdf(uploaded_file: io.BytesIO) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
