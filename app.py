import streamlit as st
import os
import io
import time
from typing import List, Dict, Any, Optional

# IMPORTANT: You must install the necessary libraries first:
# pip install streamlit google-genai pypdf

# --------------------------------------------------------------------------------------
# 1. FIREBASE & AUTH PLACEHOLDERS (REQUIRED FOR PRODUCTION)
# In a real collaborative app like PolicyPARAKH, this section would handle user state
# and secure data storage using Firebase/Firestore, but for a single-file demo,
# we use session state.
# --------------------------------------------------------------------------------------

# Placeholder for Gemini API Key (Required for the model calls)
# In a real Streamlit app, this should be set in .streamlit/secrets.toml
# For this code to run, you must set the GEMINI_API_KEY environment variable.
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --------------------------------------------------------------------------------------
# 2. CORE UTILITY FUNCTIONS
# --------------------------------------------------------------------------------------

@st.cache_resource
def initialize_gemini():
    """Initializes and returns the Gemini client."""
    from google import genai
    
    if not API_KEY:
        st.error("🚨 Gemini API Key not found. Please set the GEMINI_API_KEY environment variable or a secret.")
        return None
    
    try:
        # We use Gemini 2.5 Flash for speed (as specified in Readme.md)
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return None

def base64_encode_pdf(uploaded_file: io.BytesIO) -> str:
    """Reads the PDF file bytes and returns a base64 encoded string."""
    import base64
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def generate_risk_assessment(client, prompt: str, pdf_data: str) -> Optional[Dict[str, Any]]:
    """
    Simulates the Auditor Agent's task:
    1. Ingests the PDF (via Base64 in the content part).
    2. Scans for key details (Room Rent Capping, Co-Pay).
    3. Outputs a quantitative Risk Score (using Structured Output).
    """
    if not client:
        return None

    # This is the expected structured output from the model (The Auditor's Report)
    risk_schema = {
        "type": "OBJECT",
        "properties": {
            "risk_score_0_to_100": {"type": "INTEGER", "description": "The policy's risk score from 0 (Safest) to 100 (Highest Risk)."},
            "co_pay_clause": {"type": "STRING", "description": "Summary of the co-pay percentage or clause found in the document."},
            "room_rent_limit": {"type": "STRING", "description": "The maximum daily room rent allowed by the policy."},
            "auditor_summary": {"type": "STRING", "description": "A concise, critical summary of the major risks and exclusions found."},
        },
        "required": ["risk_score_0_to_100", "co_pay_clause", "room_rent_limit", "auditor_summary"]
    }

    # System Instruction to guide the Auditor Agent's persona and task
    system_prompt = (
        "You are the PolicyPARAKH Auditor Agent. Your task is to ruthlessly scan the provided "
        "insurance policy document for hidden risks, especially co-pay and room rent limits. "
        "Provide a score from 0 (Low Risk) to 100 (High Risk). Respond only with the requested JSON structure."
    )

    contents = [
        # Pass the PDF as inline data for multimodal processing
        {
            "inlineData": {
                "mimeType": "application/pdf",
                "data": pdf_data
            }
        },
        # Pass the user's prompt as text
        {"text": prompt}
    ]

    try:
        with st.spinner("🧠 Auditor Agent Scanning Policy..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Using Flash for fast multimodal analysis
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "response_mime_type": "application/json",
                    "response_schema": risk_schema,
                    "temperature": 0.0, # Prefer deterministic, factual output
                }
            )
        
        # The response text is a JSON string conforming to the schema
        import json
        return json.loads(response.text)

    except Exception as e:
        st.error(f"Auditor Agent failed to process document: {e}")
        return None

# --------------------------------------------------------------------------------------
# 3. STREAMLIT UI & CENTRAL CHATBOT LOGIC
# --------------------------------------------------------------------------------------

st.set_page_config(
    page_title="PolicyPARAKH: Neural Legal Defense System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for a modern, mobile-friendly look
st.markdown("""
<style>
.stApp {
    font-family: 'Inter', sans-serif;
}
h1 {
    color: #007BFF; /* Primary blue for title */
    text-align: center;
}
.stSidebar {
    background-color: #f0f2f6; /* Light gray sidebar */
    padding-top: 2rem;
}
.stAlert {
    border-radius: 0.5rem;
}
.reportview-container .main {
    padding-top: 0;
}
.stButton>button {
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    font-weight: bold;
    background-color: #28a745; /* Success green */
    color: white;
}
/* Style for the risk score meter (simulate a dashboard gauge) */
.risk-meter {
    border: 3px solid #007BFF;
    border-radius: 0.75rem;
    padding: 1.5rem;
    text-align: center;
    background-color: #e9ecef;
}
.risk-score {
    font-size: 4rem;
    font-weight: 900;
}
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)


def main():
    """The main application function (The Central Chatbot Interface)."""
    st.title("PolicyPARAKH: Neural Legal Defense System")
    st.markdown("##### The AI that reads the fine print, fights the lawyer, and predicts the future.")

    # Initialize Gemini Client
    client = initialize_gemini()
    if not client:
        return

    # ------------------ Sidebar: Input & Controls ------------------
    st.sidebar.header("Input Policy Document")

    # Policy Ingestion
    uploaded_file = st.sidebar.file_uploader(
        "Upload Insurance Policy (PDF only)",
        type="pdf",
        key="policy_pdf"
    )

    if uploaded_file and 'pdf_base64' not in st.session_state:
        # Cache the base64 data to avoid re-reading the file on every interaction
        st.session_state.pdf_base64 = base64_encode_pdf(uploaded_file)
        st.sidebar.success(f"✅ Policy '{uploaded_file.name}' ingested successfully.")
        
        # Clear the report when a new file is uploaded
        if 'auditor_report' in st.session_state:
             del st.session_state.auditor_report
             
    elif not uploaded_file:
        if 'pdf_base64' in st.session_state:
            del st.session_state.pdf_base64

    # The Core Action: Initial Auditor Scan
    if st.sidebar.button("Run Initial Auditor Scan") and uploaded_file and client:
        if 'pdf_base64' in st.session_state:
            # The prompt guides the Auditor Agent to perform the standard, defined task
            initial_prompt = (
                "Analyze the uploaded PDF policy for Room Rent Capping, Co-Pay, and major exclusions. "
                "Provide a quantitative risk score and a critical summary."
            )
            
            report = generate_risk_assessment(client, initial_prompt, st.session_state.pdf_base64)
            if report:
                st.session_state.auditor_report = report
            else:
                 st.session_state.auditor_report = None # Ensure state is clear if analysis fails

    # ------------------ Main Area: Dashboard & Chat ------------------
    
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    if 'auditor_report' in st.session_state and st.session_state.auditor_report:
        report = st.session_state.auditor_report
        
        st.header("Auditor Agent Risk Assessment")

        # 1. Risk Score Display
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Map score to color for better visual communication (Red=High Risk)
            score_val = report['risk_score_0_to_100']
            color = 'red' if score_val > 70 else ('orange' if score_val > 40 else 'green')
            
            st.markdown(f"""
            <div class='risk-meter' style='border-color: {color};'>
                <p>Policy Risk Score</p>
                <p class='risk-score' style='color: {color};'>{score_val}</p>
                <p style='font-size: 0.9rem;'>0 (Low Risk) / 100 (High Risk)</p>
            </div>
            """, unsafe_allow_html=True)

        # 2. Key Findings Summary
        with col2:
            st.subheader("Key Exclusion Findings (The Fine Print)")
            st.markdown(f"**Co-Pay Clause:** {report['co_pay_clause']}")
            st.markdown(f"**Room Rent Limit:** {report['room_rent_limit']}")
            st.markdown("---")
            st.markdown(f"**Auditor's Critical Summary:** \n\n{report['auditor_summary']}")
            
        st.markdown("---")

    # ------------------ The Unified Chatbot Interface ------------------

    st.subheader("Unified Chatbot Interface (Ask a Question)")

    # Initialize chat history (The Central Command's memory)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # The Chat Input box
    if prompt := st.chat_input("Ask about your policy, exclusions, or financial impact..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response (The Central Chatbot delegates the question)
        with st.chat_message("assistant"):
            if 'pdf_base64' not in st.session_state:
                st.warning("Please upload a PDF policy document first to run the analysis.")
                st.session_state.messages.append({"role": "assistant", "content": "Please upload a PDF policy document first to run the analysis."})
                return

            message_placeholder = st.empty()
            full_response = ""
            
            # The Central Chatbot prepares the context for the agent
            context = f"""
            The user is asking a follow-up question about their insurance policy. 
            The policy details are provided as a PDF. 
            The initial Auditor Agent report summarized the policy as: {st.session_state.auditor_report if 'auditor_report' in st.session_state and st.session_state.auditor_report else 'No initial report available.'}
            User Question: {prompt}
            
            Act as the Central Chatbot interface, synthesizing the policy document and the initial findings. 
            If the question requires financial forecasting or outside search (like crime rates), acknowledge this is a task for the 
            Architect Agent or Sentinel Agent, but provide the best answer you can using only the policy text and the initial report.
            """

            # I, the developer, will use Gemini to simulate the agent coordination.
            try:
                # Use a standard text generation call for the follow-up chat
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=context,
                    config={
                         "temperature": 0.3,
                    }
                )
                full_response = response.text
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Agent Coordination Failed: Error processing request. ({e})"
                message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
