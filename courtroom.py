import streamlit as st
from google.genai import types

def run_courtroom_simulation(client, policy_summary, user_claim):
    """
    Simulates a legal battle between a Company Lawyer and a Consumer Advocate.
    """
    system_prompt = (
        "You are the PolicyPARAKH Courtroom Engine. "
        "Generate a script for a simulated legal argument based on the policy risks and user claim. "
        "Characters: "
        "1. 🏛️ Company Lawyer (Ruthless, cites exclusions). "
        "2. 🛡️ User Advocate (Helpful, finds loopholes, cites IRDAI rules). "
        "3. ⚖️ Judge (Gives the final verdict). "
        "Format the output as a dramatic script."
    )
    
    user_prompt = f"Policy Context: {policy_summary}. User Claim Situation: {user_claim}. Fight!"

    try:
        with st.spinner("⚖️ Court is in session..."):
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7 # High creativity for drama
                )
            )
        return response.text
    except Exception as e:
        return f"Court Adjourned (Error): {e}"
