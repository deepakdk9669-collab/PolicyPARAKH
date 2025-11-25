import streamlit as st
from google.genai import types

def compare_policy(client, report):
    """
    Universal Scout: Compares Insurance, Loans, or Services.
    """
    doc_type = report.get('doc_type', 'Document')
    entity = report.get('entity_name', 'Current Provider')
    risks = report.get('bad_clauses', 'risks')
    
    system_instruction = f"""
    You are a Market Research Expert.
    The user has a {doc_type} from '{entity}' with these negatives: {risks}.
    
    Task:
    1. Use Google Search to find BETTER alternatives in the market right now (2025).
    2. If it's Insurance: Compare Premiums/Features.
    3. If it's a Contract/Service: Suggest better vendors or standard terms.
    4. If it's a Loan: Suggest banks with lower interest rates.
    
    Output a Comparison Table.
    """
    
    user_prompt = f"Find me better alternatives to {entity} for this {doc_type}. Why should I switch?"

    try:
        with st.spinner(f"🛒 Scouting market for better {doc_type}s..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
            return response.text
    except Exception as e:
        return f"Scout Error: {e}"
