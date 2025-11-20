import streamlit as st
import google.generativeai as genai

# Setup
st.set_page_config(page_title="Model Detector", layout="wide")
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("🕵️‍♂️ API Model Detector (Live)")
st.write(f"Current System Date: {time.strftime('%Y-%m-%d')}")

try:
    st.subheader("Available Models for your Key:")
    
    # List models
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"{m.name}  |  Ver: {m.version}")
            
except Exception as e:
    st.error("CRITICAL: Your google-generativeai library is too old.")
    st.code(str(e))
    st.warning("SOLUTION: Delete this app on Streamlit Cloud and deploy again to force an update.")
    

