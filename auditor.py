import streamlit as st
import json
from google.genai import types
from typing import Optional, Dict, Any

def generate_risk_assessment(client, prompt: str, file_data: str, mime_type: str = "application/pdf") -> Optional[Dict[str, Any]]:
    if not client: return None

    # Force the AI to be an Insurance Auditor, NOT a System Admin
    system_instruction = """
    You are an expert Insurance Policy Auditor. 
    Your ONLY job is to analyze insurance documents (PDFs/Images).
    
    DO NOT generate 'System Logs', 'Network Activity', or 'Security Protocols'. 
    That is wrong.
    
    Instead, extract:
    1. Insurance Company Name
    2. Co-Pay Clauses (Look for percentages user has to pay)
    3. Room Rent Limits (Look for capping on rooms)
    4. Waiting Periods
    5. A Risk Score (0-100) based on how bad the policy is for the user.
    """

    risk_schema = {
        "type": "OBJECT",
        "properties": {
            "insurance_company_name": {"type": "STRING"},
            "risk_score_0_to_100": {"type": "INTEGER"},
            "co_pay_clause": {"type": "STRING"},
            "room_rent_limit": {"type": "STRING"},
            "auditor_summary": {"type": "STRING"},
        },
        "required": ["insurance_company_name", "risk_score_0_to_100", "auditor_summary"]
    }

    try:
        # 1. Try with Gemini 2.5 Pro (Best for reasoning)
        with st.spinner("🧠 Reading Policy Document..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=file_data, mime_type=mime_type),
                            types.Part.from_text(text=prompt + " Analyze this specific insurance policy image/pdf.")
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=risk_schema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)

    except Exception as e:
        st.warning(f"⚠️ Pro Model busy, switching to Flash... ({e})")
        # 2. Fallback to Flash
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=file_data, mime_type=mime_type),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=risk_schema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e2:
            st.error(f"❌ Error: {e2}")
            return None
