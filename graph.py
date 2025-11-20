import google.generativeai as genai
import streamlit as st
from prompts import MASTER_SYSTEM_PROMPT
import tools
import random
import time

# --- KEY ROTATION LOGIC ---
def configure_random_key():
    """
    Randomly selects an API key from the secrets list.
    """
    try:
        # Fetch the list from secrets
        keys = st.secrets["API_KEYS"]
        
        if isinstance(keys, list) and len(keys) > 0:
            selected_key = random.choice(keys)
            # Configure the key
            genai.configure(api_key=selected_key)
            return True
        else:
            st.error("❌ No API Keys found in secrets.toml list.")
            return False
    except Exception as e:
        st.error(f"❌ Key Config Error: {str(e)}")
        return False

def run_audit(policy_text):
    # 1. Configure a Fresh Key
    if not configure_random_key():
        return "⚠️ System Error: Keys missing."

    # 2. Use Gemini 2.5 Pro (Since we have multiple keys now!)
    # We stick to 2.5-pro for stability, but you can try 'gemini-3-pro-preview' if you feel lucky.
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro-preview-05-06')
    except:
        model = genai.GenerativeModel('models/gemini-1.5-flash') # Safety backup

    # 3. Extract Company
    try:
        name_prompt = f"Extract only the Company Name from this text: {policy_text[:1000]}"
        company_name = model.generate_content(name_prompt).text.strip()
    except:
        company_name = "Insurance Company"

    # 4. Immortal Search
    search_query = f"{company_name} insurance claim settlement ratio complaints scam review"
    search_data = tools.immortal_search(search_query)

    # 5. Final Analysis
    final_prompt = f"""
    {MASTER_SYSTEM_PROMPT}
    
    ---
    REAL-WORLD INTELLIGENCE (From Web Search):
    {search_data}
    ---
    
    DOCUMENT TEXT TO AUDIT:
    {policy_text[:45000]} 
    """
    
    try:
        response = model.generate_content(final_prompt)
        return response.text
        
    except Exception as e:
        return f"⚠️ Analysis Failed: {str(e)}. Please try again (different key will be used)."
        
