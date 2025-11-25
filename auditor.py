import streamlit as st
import json
from google.genai import types
from typing import Optional, Dict, Any

def generate_risk_assessment(client, prompt: str, pdf_data: str) -> Optional[Dict[str, Any]]:
    if not client: return None

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
        # Switching to Gemini 2.5 Pro (Stable & Free Tier Friendly)
        with st.spinner("🧠 Auditor (Gemini 2.5 Pro) स्कैन कर रहा है..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro', 
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction="You are the Auditor Agent. Extract risks, co-pay, and room rent limits.",
                    response_mime_type="application/json",
                    response_schema=risk_schema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)

    except Exception as e:
        # Fallback to Flash if Pro is busy (Smart Logic)
        st.warning(f"⚠️ Pro Model Busy. Switching to Flash... ({e})")
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction="You are the Auditor Agent.",
                    response_mime_type="application/json",
                    response_schema=risk_schema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except:
            return None # Return None smoothly instead of crashing
