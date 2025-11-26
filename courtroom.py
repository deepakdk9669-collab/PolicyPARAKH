import streamlit as st
from google.genai import types
import tavily_search

def run_courtroom_simulation(client, policy_summary, user_claim, user_clues):
    """
    Real-World Courtroom Simulator.
    Uses Tavily to find REAL legal precedents (Case Laws) to support the argument.
    """
    
    # 1. Research Phase (Internet)
    search_query = f"Consumer court judgments India insurance claim rejection {user_claim} precedents"
    legal_research = tavily_search.tavily_deep_search(search_query)
    
    system_instruction = """
    You are the 'PolicyPARAKH Courtroom Engine'.
    Simulate a HIGH-STAKES, REALISTIC legal battle in an Indian Consumer Court.
    
    Characters:
    1. 🏛️ **Company Lawyer (Adv. Batra):** Ruthless. Cites specific policy exclusions.
    2. 🛡️ **User's Advocate (Adv. Mehra):** Sharp. Uses the 'User Clues' and REAL CASE LAWS (from research) to find loopholes.
    3. ⚖️ **Judge:** Neutral observer.
    
    Output Structure:
    1. **The Argument:** A dramatic script of the argument.
    2. **Legal Precedent:** Cite a real or similar case from the search results.
    3. **Win Probability Meter:** A percentage (0-100%) showing the user's chance of winning based on current facts.
    4. **Next Move:** Ask the user for a specific piece of evidence (e.g., "Do you have the doctor's first prescription?") to increase winning chances.
    """
    
    user_prompt = f"""
    Policy Context: {policy_summary}
    User Claim: {user_claim}
    User's Secret Clues: {user_clues}
    
    Legal Research Data: {legal_research}
    
    Start the simulation!
    """

    try:
        with st.spinner("⚖️ Researching Case Laws & Preparing Arguments..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                )
            )
            return response.text
    except Exception as e:
        return f"Court Error: {e}"
