import streamlit as st
import json
from google.genai import types
from typing import Optional, Dict, Any

def generate_risk_assessment(client, prompt: str, pdf_data: str) -> Optional[Dict[str, Any]]:
    if not client: return None

    # रिस्पॉन्स का स्ट्रक्चर
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
        # यहाँ हम सीधे Gemini 3 Pro Preview यूज़ कर रहे हैं
        with st.spinner("🧠 Auditor Agent (Gemini 3 Pro) पॉलिसी को स्कैन कर रहा है..."):
            response = client.models.generate_content(
                model='gemini-3-pro-preview', # The BEAST mode
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
                    system_instruction="You are the Auditor Agent. Extract risks, co-pay, and room rent limits with extreme precision.",
                    response_mime_type="application/json",
                    response_schema=risk_schema,
                    temperature=0.1 # High precision
                )
            )
        return json.loads(response.text)

    except Exception as e:
        st.error(f"Auditor Error (Gemini 3): {e}")
        return None
