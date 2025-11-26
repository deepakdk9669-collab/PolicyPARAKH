import streamlit as st
from google.genai import types
import search_engine
import time

def run_courtroom_simulation(client, policy_summary, user_claim, user_clues):
    """
    Real-World Interactive Courtroom Simulator.
    """
    
    # Phase 1: Legal Research (Real-Time)
    search_query = f"Consumer court judgement {user_claim} insurance India precedents rejection reasons"
    legal_data = search_engine.search_web(search_query, focus="legal")
    
    # System Instructions for the simulation
    system_instruction = """
    You are the 'PolicyPARAKH Courtroom Engine'. You must simulate a realistic Indian Consumer Court hearing.
    
    **Characters:**
    1.  **Advocate Vikram (User's Counsel):** Sharp, empathetic, uses case laws to defend the user.
    2.  **Advocate Singhania (Company Counsel):** Ruthless, sticks to policy exclusions, tries to invalidate the claim.
    3.  **Judge (Justice Rao):** Fair, neutral, asks tough questions to both sides.

    **Process:**
    1.  **Opening Statements:** Both lawyers present their initial arguments based on the policy and claim.
    2.  **Cross-Examination:** Adv. Singhania attacks the user's claim. Adv. Vikram defends using the 'User Clues' and 'Legal Data'.
    3.  **The Twist:** Introduce a critical point of contention based on real-world scenarios (e.g., 'Non-disclosure' or 'Medical necessity').
    4.  **Closing Arguments:** Final appeals from both sides.
    5.  **Judge's Analysis & Win Probability:** The Judge breaks down the strengths and weaknesses of the user's case and estimates a winning probability percentage.

    **Tone:** Professional, dramatic, yet legally grounded. Use Indian legal terminology (e.g., 'My Lord', 'Consumer Protection Act').
    """
    
    prompt = f"""
    **Case Details:**
    * **Policy Context:** {policy_summary}
    * **User's Claim:** {user_claim}
    * **User's Secret Evidence/Clues:** {user_clues}
    * **Real-World Legal Precedents found:** {legal_data}

    **Action:** Start the courtroom drama! Make it engaging and detailed. End with a clear "Verdict Prediction" section.
    """
    
    try:
        # Streaming the response for a "live" feel
        response_container = st.empty()
        full_response = ""
        
        # Using streaming to simulate the conversation flow
        response = client.models.generate_content_stream(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8 # Higher temperature for more creative/dramatic output
            )
        )
        
        for chunk in response:
            full_response += chunk.text
            response_container.markdown(full_response + "▌") # Typewriter effect
            time.sleep(0.05) # Slight delay for reading
            
        response_container.markdown(full_response) # Final output
        return full_response

    except Exception as e:
        return f"⚠️ Courtroom Error: {e}"
