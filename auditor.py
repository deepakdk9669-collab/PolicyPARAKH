import streamlit as st
import json
from google.genai import types
from typing import Optional, Dict, Any

def generate_risk_assessment(client, prompt: str, file_data: str, mime_type: str = "application/pdf") -> Optional[Dict[str, Any]]:
    if not client: return None

    # Strict System Instruction to prevent "System Audit" hallucinations
    system_instruction = """
    You are an expert Insurance Policy Auditor. 
    Analyze the provided document (PDF or Image).
    Extract:
    1. Insurance Company Name
    2. Co-Pay Clauses
    3. Room Rent Limits
    4. Risk Score (0-100)
    5. A short summary of the bad clauses.
    Output JSON.
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
        # FORCE USE of Gemini 2.5 Pro (Stable)
        # We removed the 3 Pro logic completely to avoid 429 Errors
        with st.spinner("🧠 Auditor (2.5 Pro) Analyzing..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
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

    except Exception as e:
        # Fallback to Flash only if Pro fails
        st.warning(f"⚠️ Pro Model Error: {e}. Switching to Flash.")
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
            st.error(f"❌ Scan Failed: {e2}")
            return None
