import google.generativeai as genai
import streamlit as st
from prompts import MASTER_SYSTEM_PROMPT
import tools # Imports your immortal_search

# Setup Google AI
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

def run_audit(policy_text):
    """
    The Main Execution Function called by app.py
    """
    # 1. Initialize the Model (Using the verified 1.5 Flash)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # 2. Extract Company Name for Search context (Simple extraction)
    # We do a quick pass to get the company name for the "Immortal Search"
    name_prompt = f"Extract only the Company Name from this text: {policy_text[:1000]}"
    try:
        company_name = model.generate_content(name_prompt).text.strip()
    except:
        company_name = "Insurance Company"

    # 3. Run Immortal Search (The Tool)
    # We search for recent complaints/ratio to feed into the final prompt
    search_query = f"{company_name} insurance claim settlement ratio complaints scam review"
    search_data = tools.immortal_search(search_query)

    # 4. The Universal Generation (The Master Prompt Application)
    # We combine the Policy Text + Search Data + Master Prompt
    
    final_prompt = f"""
    {MASTER_SYSTEM_PROMPT}
    
    ---
    REAL-WORLD CONTEXT (From Immortal Search):
    {search_data}
    ---
    
    DOCUMENT TEXT TO AUDIT:
    {policy_text[:40000]}
    """
    
    # 5. Generate Response
    try:
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Swarm Error: {str(e)}"
      
