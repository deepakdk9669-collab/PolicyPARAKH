import streamlit as st
from google.genai import types
import search_engine

def run_courtroom_simulation(client, policy_summary, user_claim, user_clues):
    # Research Case Laws
    legal_data = search_engine.search_web(f"Consumer court judgement {user_claim} insurance India precedents")
    
    system_instruction = """
    You are a Courtroom Simulator.
    Create a dramatic dialogue between a Company Lawyer and User Advocate.
    Use the provided Legal Data to cite real precedents.
    End with a 'Win Probability'.
    """
    
    prompt = f"""
    Policy: {policy_summary}
    Claim: {user_claim}
    Clues: {user_clues}
    Legal Data: {legal_data}
    """
    
    try:
        res = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
        )
        return res.text
    except: return "Courtroom is busy."
