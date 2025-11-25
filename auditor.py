import streamlit as st
import json
from typing import Optional, Dict, Any

def generate_risk_assessment(client, prompt: str, pdf_data: str) -> Optional[Dict[str, Any]]:
    """
    Auditor Agent Task:
    1. Ingests PDF.
    2. Scans for Room Rent Capping, Co-Pay, and Company Name.
    3. Outputs Risk Score.
    """
    if not client:
        return None

    # Structured Output Schema
    risk_schema = {
        "type": "OBJECT",
        "properties": {
            "insurance_company_name": {"type": "STRING", "description": "The name of the insurance provider found in the document."},
            "risk_score_0_to_100": {"type": "INTEGER", "description": "Risk score from 0 (Safe) to 100 (High Risk)."},
            "co_pay_clause": {"type": "STRING", "description": "Summary of co-pay percentage."},
            "room_rent_limit": {"type": "STRING", "description": "Maximum daily room rent allowed."},
            "auditor_summary": {"type": "STRING", "description": "Critical summary of risks."},
        },
        "required": ["insurance_company_name", "risk_score_0_to_100", "co_pay_clause", "room_rent_limit", "auditor_summary"]
    }

    system_prompt = (
        "You are the PolicyPARAKH Auditor Agent. Ruthlessly scan the insurance policy "
        "for hidden risks. Identify the Company Name correctly. Provide a score from 0 to 100."
    )

    contents = [
        {"inlineData": {"mimeType": "application/pdf", "data": pdf_data}},
        {"text": prompt}
    ]

    try:
        with st.spinner("🧠 Auditor Agent Scanning Policy..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "response_mime_type": "application/json",
                    "response_schema": risk_schema,
                    "temperature": 0.0,
                }
            )
        return json.loads(response.text)

    except Exception as e:
        st.error(f"Auditor Agent failed: {e}")
        return None
