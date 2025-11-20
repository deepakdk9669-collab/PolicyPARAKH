import google.generativeai as genai
import streamlit as st
from prompts import MASTER_SYSTEM_PROMPT
import tools
import random
import time
from google.api_core import exceptions

# --- 1. ROBUST RETRY ENGINE ---
def run_with_rotation(func_to_run):
    """
    Tries to execute 'func_to_run' using every single API key in the list.
    If Key 1 fails (429), it immediately switches to Key 2, then Key 3...
    """
    try:
        # Load keys from secrets
        keys = st.secrets["API_KEYS"]
        if not isinstance(keys, list):
            keys = [st.secrets["GOOGLE_API_KEY"]]
    except:
        return "❌ System Error: API Keys not found in secrets."

    # Randomize order to distribute load
    random.shuffle(keys)
    
    last_error = None

    # THE LOOP
    for i, key in enumerate(keys):
        try:
            # 1. Configure specific key
            genai.configure(api_key=key)
            
            # 2. Try to run the function
            return func_to_run()
            
        except exceptions.ResourceExhausted:
            # This is the 429 Error. Log it and CONTINUE to next key.
            # print(f"Key {i} Exhausted. Switching...") 
            last_error = f"Key {i} Quota Exceeded"
            continue 
            
        except Exception as e:
            # If it's a model not found error, also switch key/model
            last_error = str(e)
            continue

    # If we exit the loop, ALL keys failed
    return f"⚠️ All API Keys Failed. Last Error: {last_error}"

# --- 2. MAIN AUDIT FUNCTION ---
def run_audit(policy_text):
    
    # Step A: Extract Company Name (Cheap Model)
    def get_name():
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        return model.generate_content(f"Extract Company Name: {policy_text[:1000]}").text.strip()
    
    # Run extraction
    company_name = run_with_rotation(get_name)
    if "⚠️" in company_name: company_name = "Insurance Company"

    # Step B: Immortal Search
    search_query = f"{company_name} insurance claim settlement ratio reviews scam"
    search_data = tools.immortal_search(search_query)

    # Step C: The Heavy Audit (Using GEMINI 2.5 PRO)
    final_prompt = f"""
    {MASTER_SYSTEM_PROMPT}
    
    ---
    LIVE MARKET INTELLIGENCE:
    {search_data}
    ---
    
    DOCUMENT TEXT:
    {policy_text[:45000]} 
    """

    def generate_audit():
        # CORRECT MODEL ID from your Screenshot
        # This is the Stable version, which should have the Free Tier active.
        model = genai.GenerativeModel('models/gemini-2.5-pro') 
        
        response = model.generate_content(final_prompt)
        return response.text

    # Run with True Rotation
    return run_with_rotation(generate_audit)
    
