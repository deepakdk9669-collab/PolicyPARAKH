import streamlit as st
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from PyPDF2 import PdfReader
import random
import time

# --- 1. UI CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="PolicyPARAKH Universal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Attractive" UI
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #4F8BF9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4F8BF9;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #4F8BF9;
    }
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #464b5c;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SECRETS & SETUP ---
def get_secret(key_name):
    try:
        return st.secrets[key_name]
    except:
        return None

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. AGENT TOOLS (THE BRAIN) ---
def immortal_search(query):
    """Robust search that tries DuckDuckGo first, then Tavily."""
    ddg = DuckDuckGoSearchRun()
    try:
        # Attempt 1: DuckDuckGo (Free)
        return f"[Source: DuckDuckGo] {ddg.invoke(query)}"
    except:
        # Attempt 2: Tavily (Backup)
        if TAVILY_API_KEY:
            try:
                tavily = TavilySearchResults(api_key=TAVILY_API_KEY)
                return f"[Source: Tavily] {str(tavily.invoke(query))}"
            except:
                pass
    return "⚠️ Search unavailable (Network/Quota). Relying on internal logic."

# --- 4. CORE ANALYSIS LOGIC ---
def analyze_policy_modern(text):
    """
    Main Agent Logic using Gemini 1.5 Flash.
    Returns: Dictionary with 'score', 'summary', 'risks', 'verdict', 'raw_report'
    """
    
    # 1. Identify Document Type
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    type_prompt = f"""
    You are an expert classifier. Classify this document text into ONE category: 
    HEALTH, MOTOR, LIFE, or CONTRACT.
    Only return the word.
    
    Text snippet: {text[:1000]}...
    """
    
    try:
        doc_type = model.generate_content(type_prompt).text.strip().upper()
    except:
        doc_type = "CONTRACT" # Fallback

    # 2. Extract Company Name for Search
    company_prompt = f"Extract only the Insurance Company Name from this text: {text[:500]}"
    company = model.generate_content(company_prompt).text.strip()
    
    # 3. Perform Background Search
    search_query = f"{company} insurance claim settlement ratio complaints 2024"
    search_data = immortal_search(search_query)

    # 4. The Deep Audit Prompt
    system_prompt = f"""
    You are PolicyPARAKH, the ultimate insurance auditor.
    
    DOCUMENT TYPE: {doc_type}
    SEARCH DATA: {search_data}
    
    Your Goal: Find the hidden traps that agents don't tell you.
    
    Analyze the full text below and output a structured report.
    
    Output Format (Strictly follow this):
    
    ## 📊 Risk Score
    [Give a number between 0-100, where 100 is safest, 0 is a scam]
    
    ## 🛡️ Verdict
    [One word: SAFE, CAUTION, or DANGEROUS]
    
    ## 🚩 Critical Red Flags
    * [Flag 1]
    * [Flag 2]
    
    ## 📝 Executive Summary
    [A simple 3-line summary for a 10-year-old]
    
    ## 🔍 Clause-by-Clause Deep Dive
    [Detailed analysis of Room Rent, Co-Pay, Exclusions, etc.]
    
    ## 💡 "What If" Scenario
    [Create a realistic bad scenario relevant to {doc_type} and calculate the loss]
    """
    
    response = model.generate_content(f"{system_prompt}\n\nDOCUMENT TEXT:\n{text}")
    return response.text, doc_type

# --- 5. FRONTEND (THE UI) ---

def main():
    # Sidebar
    with st.sidebar:
        st.title("🛡️ PolicyPARAKH")
        st.markdown("---")
        st.caption("Status: **Universal Swarm Mode**")
        
        if GOOGLE_API_KEY:
            st.success("✅ Neural Engine: Online")
        else:
            st.error("❌ API Key Missing")
            
        st.markdown("### 🧠 Capabilities")
        st.info("Reading The Fine Print So You Don't Have To.")
        st.markdown("---")
        st.markdown("Built by **PanelScripter Core**")

    # Main Hero Section
    st.title("PolicyPARAKH Universal")
    st.markdown("### 🚀 Upload your Policy PDF to Audit")
    
    uploaded_file = st.file_uploader("", type="pdf")

    if uploaded_file is not None:
        # Initialize Session State for Chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "audit_done" not in st.session_state:
            st.session_state.audit_done = False
        if "full_text" not in st.session_state:
            st.session_state.full_text = ""
        
        # READ PDF
        if not st.session_state.audit_done:
            with st.status("🕵️‍♂️ Swarm Agents Working...", expanded=True) as status:
                st.write("📄 Reading PDF Binary...")
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                st.session_state.full_text = text
                
                st.write("🧠 Classifying & analyzing risk vectors...")
                # CALL THE NEW LOGIC
                try:
                    report, doc_type = analyze_policy_modern(text)
                    st.session_state.report = report
                    st.session_state.doc_type = doc_type
                    status.update(label="✅ Audit Complete!", state="complete", expanded=False)
                    st.session_state.audit_done = True
                except Exception as e:
                    st.error(f"Critical Failure: {e}")
                    st.stop()

        # DISPLAY RESULTS (The "Better UI" part)
        if st.session_state.audit_done:
            report = st.session_state.report
            
            # Try to extract Score and Verdict for the top metrics
            try:
                # Simple parsing (Robust enough for this demo)
                score_line = [line for line in report.split('\n') if "Risk Score" in line or "0-100" in line][0]
                # Extract number roughly
                import re
                score = re.findall(r'\d+', score_line.split('\n')[1] if '\n' in score_line else report)
                final_score = score[0] if score else "N/A"
            except:
                final_score = "Check Report"

            # Dashboard Row
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Doc Type", value=st.session_state.doc_type)
            with col2:
                st.metric(label="Calculated Safety Score", value=f"{final_score}/100")
            with col3:
                st.metric(label="AI Agent Verdict", value="Processing...")
            
            st.divider()

            # TABS LAYOUT
            tab1, tab2, tab3 = st.tabs(["📊 Visual Report", "💬 Chat with Policy", "📜 Raw Data"])
            
            with tab1:
                st.markdown(report)
                
            with tab2:
                st.header("💬 Ask the Swarm")
                st.caption("Ask anything about specific clauses (e.g., 'What is the waiting period?')")
                
                # Chat History Display
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Chat Input
                if prompt := st.chat_input("Ask a specific question about this policy..."):
                    # User message
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # Assistant Response
                    with st.chat_message("assistant"):
                        chat_model = genai.GenerativeModel('gemini-1.5-flash')
                        # Contextualize with the policy text
                        full_prompt = f"Context: {st.session_state.full_text}\n\nUser Question: {prompt}\n\nAnswer strictly based on the context provided."
                        
                        stream_res = chat_model.generate_content(full_prompt)
                        response = stream_res.text
                        st.markdown(response)
                        
                    st.session_state.messages.append({"role": "assistant", "content": response})

            with tab3:
                with st.expander("View Extracted Text"):
                    st.text(st.session_state.full_text)

if __name__ == "__main__":
    main()
    
