import streamlit as st
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from PyPDF2 import PdfReader
import time

# --- 1. UI CONFIGURATION (Professional Look) ---
st.set_page_config(
    page_title="PolicyPARAKH | AI Audit",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for Professional Styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #FFFFFF;
    }
    .stAlert {
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #4F8BF9;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SETUP & API KEYS ---
def get_secret(key_name):
    try:
        return st.secrets[key_name]
    except:
        return None

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 3. HELPER FUNCTIONS ---
def analyze_policy_v2(text):
    """Uses Gemini 1.5 Flash for fast, accurate audit."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt for Professional Audit
    system_prompt = """
    You are a Senior Insurance Auditor suitable for a Legal Hackathon.
    Analyze the provided policy document rigorously.
    
    OUTPUT FORMAT:
    
    ### 🛡️ Executive Verdict
    **Risk Score:** [0-100]
    **Status:** [SAFE / CAUTION / HIGH RISK]
    
    ### 🚩 Critical Red Flags
    * [Flag 1 with page reference inference]
    * [Flag 2]
    
    ### 💰 Financial Hidden Traps
    * **Room Rent Capping:** [Details]
    * **Co-Pay:** [Details]
    * **Disease Waiting Periods:** [Details]
    
    ### ⚖️ Legal Loophole Analysis
    [Analyze ambiguous terms that could lead to claim rejection]
    """
    
    try:
        response = model.generate_content(f"{system_prompt}\n\nPOLICY TEXT: {text[:30000]}")
        return response.text
    except Exception as e:
        return f"Error in AI Analysis: {str(e)}"

# --- 4. MAIN UI FLOW ---

def main():
    # -- SIDEBAR --
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2230/2230606.png", width=50)
        st.title("PolicyPARAKH")
        st.caption("v2.1 | Universal Build")
        st.markdown("---")
        st.markdown("**System Status:**")
        if GOOGLE_API_KEY:
            st.success("🟢 AI Engine Ready")
        else:
            st.error("🔴 API Key Missing")
        
        st.info("This tool uses **Gemini 1.5 Flash** for legal-grade document analysis.")

    # -- MAIN AREA --
    st.title("⚖️ PolicyPARAKH: Automated Policy Auditor")
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #4F8BF9; margin-bottom: 20px;'>
        <h4 style='margin:0; color: white;'>Upload your Insurance Policy PDF</h4>
        <p style='margin:0; color: #A0A0A0; font-size: 14px;'>The AI will extract hidden clauses, calculate risk scores, and identify rejection traps.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type="pdf")

    if uploaded_file:
        # Processing UI
        with st.status("🔄 Initializing Audit Protocols...", expanded=True) as status:
            st.write("📂 Extracting text layer from PDF...")
            try:
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                
                st.write(f"✅ Extracted {len(text)} characters.")
                
                st.write("🧠 Running Gemini 1.5 Flash Analysis...")
                report = analyze_policy_v2(text)
                
                status.update(label="✅ Audit Completed Successfully", state="complete", expanded=False)
                
                # --- RESULT DASHBOARD ---
                st.divider()
                st.subheader("📊 Audit Report")
                st.markdown(report)
                
            except Exception as e:
                st.error(f"⚠️ System Error: {e}")
                st.warning("Please check if 'gemini-1.5-flash' is supported by your API Key or Library version.")

if __name__ == "__main__":
    main()

