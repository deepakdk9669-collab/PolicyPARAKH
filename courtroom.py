import streamlit as st
from google.genai import types

def run_courtroom_simulation(client, policy_summary, user_claim):
    system_instruction = """
    You are the Virtual Courtroom Engine.
    Simulate a dramatic legal battle.
    
    Characters:
    1. 🏛️ Company Lawyer: Uses the policy text to reject the claim.
    2. 🛡️ User Advocate: Uses REAL-TIME Google Search to find 'Consumer Court Judgments' favoring the user.
    3. ⚖️ Judge: Decides based on logic.
    
    Output a Script format.
    """
    
    user_prompt = f"Policy Context: {policy_summary}. User Claim: {user_claim}. Find similar court cases online and fight!"

    try:
        with st.spinner("⚖️ Researching Legal Precedents (Online)..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())], # Real-Time Legal Search
                    temperature=0.7
                )
            )
            return response.text
    except Exception as e:
        return f"Court Error: {e}"
