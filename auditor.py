import streamlit as st
import json
from google.genai import types
from typing import Optional, Dict, Any

def identify_document_type(client, file_data, mime_type):
    """
    Step 1: Detects if the file is Insurance, Contract, or Loan.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=file_data, mime_type=mime_type),
                        types.Part.from_text(text="Classify this document into one word: 'Insurance', 'Contract', 'Loan', or 'Other'. Return ONLY the word.")
                    ]
                )
            ]
        )
        return response.text.strip()
    except:
        return "Other"

def generate_risk_assessment(client, prompt: str, file_data: str, mime_type: str = "application/pdf") -> Optional[Dict[str, Any]]:
    if not client: return None

    # Step 1: Auto-Detect Document Type
    doc_type = identify_document_type(client, file_data, mime_type)
    
    # Step 2: Switch Persona based on Type (LangChain Style Routing)
    if "Insurance" in doc_type:
        role = "Insurance Auditor"
        focus = "Co-Pay, Room Rent Limits, Waiting Periods, and Exclusions."
    elif "Contract" in doc_type or "Agreement" in doc_type:
        role = "Senior Corporate Lawyer"
        focus = "Dangerous Loopholes, Unfair Termination Clauses, Indemnity, and Hidden Liabilities."
    elif "Loan" in doc_type:
        role = "Financial Risk Analyst"
        focus = "Hidden Processing Fees, Variable Interest Traps, and Foreclosure Charges."
    else:
        role = "Universal Document Analyzer"
        focus = "Key Risks and Summary."

    # Dynamic System Instruction
    system_instruction = f"""
    You are an expert {role}.
    
    Analyze the uploaded {doc_type}.
    Your Goal: Protect the user. Find what they are missing.
    
    Extract these specific details in JSON:
    1. 'entity_name': (Company/Party Name)
    2. 'risk_score_0_to_100': (Higher means more dangerous for the user)
    3. 'bad_clauses': (List of loopholes/negatives)
    4. 'good_points': (List of plus points/benefits)
    5. 'summary': (Critical verdict)
    """

    risk_schema = {
        "type": "OBJECT",
        "properties": {
            "entity_name": {"type": "STRING"},
            "risk_score_0_to_100": {"type": "INTEGER"},
            "bad_clauses": {"type": "STRING", "description": "Comma separated list of bad clauses/loopholes"},
            "good_points": {"type": "STRING", "description": "Comma separated list of beneficial clauses"},
            "summary": {"type": "STRING"},
        },
        "required": ["entity_name", "risk_score_0_to_100", "bad_clauses", "good_points", "summary"]
    }

    try:
        with st.spinner(f"🧠 {role} analyzing {doc_type}..."):
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=file_data, mime_type=mime_type),
                            types.Part.from_text(text=f"Analyze this {doc_type}. Find loopholes and pros/cons.")
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
            result = json.loads(response.text)
            result['doc_type'] = doc_type # Store type for other agents
            return result

    except Exception as e:
        st.error(f"Analysis Failed: {e}")
        return None
