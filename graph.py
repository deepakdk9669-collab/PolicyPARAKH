import google.generativeai as genai
import streamlit as st
from prompts import MASTER_SYSTEM_PROMPT
import tools

# Setup
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

def run_audit(policy_text):
    # 🔥 CHANGED: Using the Most Advanced Model Available
    model = genai.GenerativeModel('models/gemini-3-pro-preview')
    
    # 1. Extract Company Name
    try:
        name_prompt = f"Extract only the Company Name from this text: {policy_text[:1000]}"
        company_name = model.generate_content(name_prompt).text.strip()
    except:
        company_name = "Insurance Company"

    # 2. Immortal Search (Deep Check)
    search_query = f"{company_name} insurance claim settlement ratio complaints scam review"
    search_data = tools.immortal_search(search_query)

    # 3. The Universal Generation
    final_prompt = f"""
    {MASTER_SYSTEM_PROMPT}
    
    ---
    REAL-WORLD INTELLIGENCE (From Web Search):
    {search_data}
    ---
    
    DOCUMENT TEXT TO AUDIT:
    {policy_text[:50000]} 
    """
    # Note: Increased text limit to 50k characters because Pro can handle it
    
    try:
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        # Fallback mechanism in case Experimental model is unstable
        return f"⚠️ Gemini 3 Error: {str(e)}. Try switching back to 2.5-flash if this persists."
        
      
