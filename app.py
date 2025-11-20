import streamlit as st
import google.generativeai as genai
import time # <--- यह Missing था

# Setup
st.set_page_config(page_title="Model Detector", layout="wide")

# Secrets handling
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key not found in Secrets!")
    st.stop()

st.title("🕵️‍♂️ API Model Detector (Live)")
st.write(f"Current System Date: {time.strftime('%Y-%m-%d')}")

try:
    st.subheader("Available Models for your Key:")
    
    # List models
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"{m.name}  |  Ver: {m.version}")
            found_any = True
            
    if not found_any:
        st.warning("No content generation models found.")

except Exception as e:
    st.error("CRITICAL: Your google-generativeai library is too old.")
    st.code(str(e))
    st.warning("SOLUTION: Delete this app on Streamlit Cloud and deploy again to force an update.")
