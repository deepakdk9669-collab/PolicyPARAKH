import streamlit as st
from google.genai import types
import json

def review_report(client, original_report, pdf_text_snippet):
    """
    The Critic Agent reviews the Auditor's findings.
    It acts as a 'Quality Control' layer (Reflexion).
    """
    system_instruction = """
    You are the Critic Agent (Quality Control).
    Your job is to review the Auditor's Insurance Analysis Report.
    
    Check for:
    1. Hallucinations (Did the Auditor make things up?)
    2. Missed Critical Risks (Did they miss a waiting period?)
    3. Severity (Is the Risk Score too low for a bad policy?)
    
    If the report is Good, return it as is.
    If Bad, add a 'CRITIC_WARNING' field to the JSON.
    """
    
    prompt = f"""
    Original Auditor Report: {original_report}
    Document Snippet (First 1000 chars): {pdf_text_snippet}
    
    Review this. Output the refined JSON.
    """

    try:
        with st.spinner("🧐 Critic Agent reviewing the report..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            return json.loads(response.text)
    except:
        return original_report # Fallback to original if Critic fails
