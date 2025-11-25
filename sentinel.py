import streamlit as st
from google.genai import types
from typing import Dict, Any

def sentinel_agent_check(client, policy_details: Dict[str, Any], query: str) -> str:
    if not client: return "Client Error"

    company_name = policy_details.get('insurance_company_name', 'Insurance Company')
    risk_summary = policy_details.get('auditor_summary', 'risks')
    
    full_prompt = f"Company: {company_name}. Risks: {risk_summary}. User Query: {query}. Search for scams, lawsuits, or settlement ratios."

    try:
        with st.spinner(f"🕵️ Sentinel (Gemini 2.5) लाइव डेटा खोज रहा है..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Best for Search Tools currently
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
            return response.text

    except Exception as e:
        return f"Sentinel Error: {e}"
