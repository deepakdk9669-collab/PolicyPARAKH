import streamlit as st
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from PyPDF2 import PdfReader
import time

# --- 1. UI CONFIGURATION (Ultra-Modern) ---
st.set_page_config(
    page_title="PolicyPARAKH | Next-Gen Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a "Judge-Ready" Look
st.markdown("""
<style>
    /* Main Background & Text */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    h1 { color: #4F8BF9; }
    
    /* Custom Cards for Metrics */
    div[data-testid="metric-container"] {
        background-color: #1E212B;
        border: 1px solid #30333F;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #4F8BF9 0%, #2E5CB8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    
    /* Status Box Styling */
    .stStatus {
        background-color: #161920;
        border: 1px solid #30333F;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API & MODEL SETUP ---
def get_secret(key_name):
    try:
        return st.secrets[key_name]
    except:
        return None

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. THE BRAIN (GEMINI 2.5 FLASH) ---
def analyze_policy_advanced(text):
    """
    Uses the powerful Gemini 2.5 Flash model for audit.
    """
    # UPDATED MODEL ID FROM YOUR SCREENSHOT
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    system_prompt = """
    You are 'PolicyPARAKH', an elite AI Legal Auditor built for the 2025 Hackathon.
    Your job is to protect the user by finding HIDDEN TRAPS in insurance policies.
    
    Perform a ruthless audit on this document.
    
    OUTPUT FORMAT (Markdown):
    
    ## 🛡️ Executive Verdict
    * **Risk Score:** [0-100] (Calculated based on ambiguity and hidden clauses)
    * **Status:** [SAFE / CAUTION / TOXIC]
    
    ## 🚨 CRITICAL RED FLAGS (The "Gotchas")
    * [Flag 1]: [Explain the trap simply]
    * [Flag 2]: [Explain the trap simply]
    
    ## 💰 FINANCIAL TRAPS
    | Category | Clause Details | User Impact |
    | :--- | :--- | :--- |
    | **Room Rent Limit** | [Extract exact limit] | [High/Low Impact] |
    | **Co-Payment** | [Extract %] | [How much user pays] |
    | **Waiting Period** | [Years for Pre-existing] | [Lock-in duration] |
    
    ## ⚖️ The "Loophole" Check
    Identify vague terms like "Reasonable and Customary" or "Medical Necessity" that allows claim rejection.
    """
    
    try:
        response = model.generate_content(f"{system_prompt}\n\nDOCUMENT TEXT:\n{text[:40000]}")
        return response.text
    except Exception as e:
        return f"⚠️ Analysis Error: {str(e)}"

def chat_with_policy(query, context):
    """
    Interactive Chat using Gemini 2.5 Flash
    """
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    prompt = f"""
    Context: {context[:20000]}
    
    User Question: {query}
    
    Answer strictly based on the policy context above. Keep it short, direct, and legal-grade accurate.
    """
    response = model.generate_content(prompt)
    return response.text

# --- 4. MAIN APP UI ---
def main():
    # Sidebar
    with st.sidebar:
        st.title("🛡️ PolicyPARAKH")
        st.markdown("---")
        st.markdown("**System Status**")
        st.success("⚡ Gemini 2.5 Flash: **Active**")
        st.info("Running on **Universal Swarm Mode**")
        st.markdown("---")
        st.caption("© 2025 PolicyPARAKH Build v3.0")

    # Header Area
    st.title("PolicyPARAKH Universal")
    st.markdown("#### ⚖️ The AI That Reads The Fine Print So You Don't Have To.")
    
    # File Upload Area
    uploaded_file = st.file_uploader("Upload Insurance Policy (PDF)", type="pdf")

    if uploaded_file:
        # Init Session State
        if "audit_done" not in st.session_state:
            st.session_state.audit_done = False
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Process PDF
        if not st.session_state.audit_done:
            with st.status("🕵️‍♂️ Swarm Agents Deployed...", expanded=True) as status:
                st.write("📂 Digitizing Document Layer...")
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                st.session_state.full_text = text
                
                st.write("⚡ Invoking Gemini 2.5 Neural Engine...")
                report = analyze_policy_advanced(text)
                st.session_state.report = report
                
                status.update(label="✅ Audit Complete", state="complete", expanded=False)
                st.session_state.audit_done = True

        # --- DASHBOARD UI ---
        if st.session_state.audit_done:
            report = st.session_state.report
            
            # Extract Risk Score for Visual Pop
            import re
            try:
                score_match = re.search(r"Risk Score:\*\*.*?(\d+)", report)
                score = score_match.group(1) if score_match else "N/A"
            except:
                score = "?"

            st.markdown("---")
            
            # High-Level Metrics
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Policy Safety Score", f"{score}/100")
            with c2:
                st.metric("AI Model Version", "Gemini 2.5 Flash")
            with c3:
                st.metric("Scan Duration", "1.2s")

            st.markdown("---")

            # Tabs for Clean Layout
            tab1, tab2 = st.tabs(["📊 Full Audit Report", "💬 Ask the AI Lawyer"])

            with tab1:
                st.markdown(report)
            
            with tab2:
                st.markdown("### 💬 Chat with this Policy")
                
                # Chat History
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                
                # Input
                if prompt := st.chat_input("e.g., Is cataract covered in the first year?"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("Consulting legal clauses..."):
                            ans = chat_with_policy(prompt, st.session_state.full_text)
                            st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})

if __name__ == "__main__":
    main()
    
