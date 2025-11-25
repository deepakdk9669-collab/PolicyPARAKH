import streamlit as st
from google.genai import types

def compare_policy(client, policy_details):
    """
    Compares the user's policy against top market standards.
    """
    system_prompt = (
        "You are the PolicyPARAKH Market Scout. "
        "Compare the uploaded policy details against the 'Gold Standard' policies in India (like HDFC Ergo Optima Secure, Niva Bupa ReAssure, etc.). "
        "Create a Comparison Table showing where the user's policy fails."
    )
    
    user_prompt = f"User Policy Details: {policy_details}. Tell me if I should switch."

    try:
        with st.spinner("🛒 Scouting the market for better options..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
        return response.text
    except Exception as e:
        return f"Market Scout Error: {e}"
