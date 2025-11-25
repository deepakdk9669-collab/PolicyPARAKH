import streamlit as st
from typing import Dict, Any

def sentinel_agent_check(client, policy_details: Dict[str, Any], query: str) -> str:
    """
    Sentinel Agent Task:
    Performs a 'Deep Dive' search on the specific Insurance Company found in the report.
    Checks: Claim Settlement Ratio, Recent Fraud, Regulatory Penalties.
    """
    if not client:
        return "Sentinel Agent: Client unavailable."

    # Extract the company name to focus the search
    company_name = policy_details.get('insurance_company_name', 'the insurance provider')
    risk_summary = policy_details.get('auditor_summary', 'No summary available.')
    
    # We construct a "Investigative Journalist" style prompt
    system_prompt = (
        "You are the PolicyPARAKH Sentinel Agent. "
        "Your goal is to protect the user by finding NEGATIVE news or WARNINGS. "
        "1. Search for the latest 'Claim Settlement Ratio' of this specific insurer. "
        "2. Search for 'consumer complaints' or 'rejected claims' news in 2024-2025. "
        "3. Synthesize this real-time data to answer the user's query."
    )

    full_prompt = (
        f"The policy is from {company_name}. "
        f"The Auditor found these risks: {risk_summary}. "
        f"The user asked: '{query}'. "
        "Use Google Search to find the company's latest track record. "
        "Be blunt and direct about any red flags."
    )

    try:
        with st.spinner(f"🕵️ Sentinel Agent investigating {company_name}..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[{"text": full_prompt}],
                config={
                    "system_instruction": system_prompt,
                    "tools": [{"google_search": {}}], # The Real-Time Engine
                    "temperature": 0.3
                }
            )
            return response.text

    except Exception as e:
        return f"Sentinel Agent Investigation Failed: {e}"
