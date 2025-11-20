import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
from langchain_google_community import GoogleSearchAPIWrapper
from PyPDF2 import PdfReader
import os
import random
from tenacity import retry, stop_after_attempt, wait_fixed

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="PolicyPARAKH", page_icon="🛡️", layout="wide")

# Robust Secret Retrieval (Handles missing keys gracefully)
def get_secret(key_name):
    try:
        return st.secrets[key_name]
    except:
        return None

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")
GOOGLE_CSE_ID = get_secret("GOOGLE_CSE_ID")
GOOGLE_SEARCH_KEY = get_secret("GOOGLE_SEARCH_API_KEY")

# Setup Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. THE IMMORTAL SEARCH TOOL ---
def immortal_search(query):
    """
    Tries DuckDuckGo -> Google -> Tavily -> Fallback.
    """
    results = []
    
    # Attempt 1: DuckDuckGo (Free)
    try:
        ddg = DuckDuckGoSearchRun()
        res = ddg.invoke(query)
        if res: return f"[Source: DuckDuckGo] {res}"
    except:
        pass

    # Attempt 2: Tavily (Backup)
    if TAVILY_API_KEY:
        try:
            tavily = TavilySearchResults(api_key=TAVILY_API_KEY)
            res = tavily.invoke(query)
            if res: return f"[Source: Tavily] {str(res)}"
        except:
            pass

    return "⚠️ Search unavailable (Network/Quota). Relying on internal logic."

# --- 3. THE "UNIVERSAL" BRAIN (PROMPTS) ---
def get_system_prompt(doc_type):
    base_prompt = """
    You are PolicyPARAKH, an expert Legal Auditor. 
    Your job is to protect the user by finding HIDDEN TRAPS in this document.
    """
    
    if doc_type == "HEALTH":
        return base_prompt + """
        FOCUS ON:
        1. Room Rent Capping (Look for '1% of Sum Insured' or specific limits).
        2. Co-Payment (Does user pay % of claim?).
        3. Waiting Periods (Specific diseases like Hernia/Cataract).
        4. Exclusions (What is NOT covered?).
        """
    elif doc_type == "MOTOR":
        return base_prompt + """
        FOCUS ON:
        1. IDV (Insured Declared Value) - Is it too low?
        2. Zero Depreciation (Is it included?).
        3. Engine Protection (Is water damage covered?).
        4. Deductibles (Compulsory amount).
        """
    elif doc_type == "LIFE":
        return base_prompt + """
        FOCUS ON:
        1. Suicide Clause (Waiting period).
        2. Claim Settlement Ratio (Mention recent data).
        3. Accidental Death Benefit definitions.
        """
    else: # CONTRACT
        return base_prompt + """
        FOCUS ON:
        1. Data Privacy (Do they sell data?).
        2. Termination (Can they cancel without cause?).
        3. Auto-Renewal (Hidden subscriptions).
        4. Arbitration (Can you sue them?).
        """

# --- 4. CORE LOGIC: CLASSIFY & ANALYZE ---
def analyze_document(text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Step A: Classify
    classification_prompt = f"""
    Classify this document into ONE category: HEALTH, MOTOR, LIFE, or CONTRACT.
    Only return the word.
    
    Document Extract: {text[:1000]}...
    """
    try:
        doc_type = model.generate_content(classification_prompt).text.strip().upper()
    except:
        doc_type = "CONTRACT" # Default
    
    # Step B: Search (The Investigator)
    # We simulate an agent searching for context
    search_query = ""
    if "insurance" in text.lower():
        # Extract company name roughly
        company_prompt = f"Extract only the Insurance Company Name from this text: {text[:500]}"
        company = model.generate_content(company_prompt).text.strip()
        search_query = f"{company} insurance claim settlement ratio complaints 2024"
    
    search_data = immortal_search(search_query) if search_query else "No external data needed."

    # Step C: The Deep Audit
    final_prompt = f"""
    {get_system_prompt(doc_type)}
    
    CONTEXT FROM WEB SEARCH:
    {search_data}
    
    DOCUMENT TEXT:
    {text}
    
    OUTPUT FORMAT (Markdown):
    # 🛡️ PolicyPARAKH Audit: {doc_type} Mode
    **Risk Score:** [0-100]/100
    
    ## 🚨 Critical Red Flags (The Traps)
    * [Flag 1]
    * [Flag 2]
    
    ## ⚖️ The Verdict
    [Safe/Caution/Dangerous]
    
    ## 🔍 Clause-by-Clause Analysis
    [Detailed breakdown]
    
    ## 💡 "What If?" Scenario
    (Create a realistic bad scenario relevant to this doc type and calculate the loss).
    """
    
    response = model.generate_content(final_prompt)
    return response.text

# --- 5. THE UI (FRONTEND) ---
def main():
    st.title("🛡️ PolicyPARAKH Universal")
    st.markdown("**The AI That Reads The Fine Print So You Don't Have To.**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Control Panel")
        st.info("Running in: Universal Swarm Mode")
        st.markdown("---")
        st.write("✅ **Health** (Room Rent, Co-pay)")
        st.write("✅ **Motor** (IDV, Zero-Dep)")
        st.write("✅ **Life** (Suicide Clause)")
        st.write("✅ **Contracts** (Privacy, Renewal)")

    # File Upload
    uploaded_file = st.file_uploader("Upload your Policy PDF", type="pdf")

    if uploaded_file is not None:
        # Show loading spinner
        with st.status("🕵️‍♂️ Swarm Agents Activated...", expanded=True) as status:
            st.write("📄 Reading Document...")
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            st.write("🧠 Classifying Document Type...")
            st.write("🌐 Checking 'Immortal' Search Tools...")
            
            # Run Analysis
            if GOOGLE_API_KEY:
                report = analyze_document(text)
                status.update(label="Audit Complete!", state="complete", expanded=False)
                
                # Display Report
                st.markdown("---")
                st.markdown(report)
                
                # Interactive Chat
                st.markdown("---")
                st.subheader("💬 Ask the Swarm")
                user_question = st.text_input("Example: 'What happens if I crash my car?' or 'Is there a waiting period?'")
                if user_question:
                    chat_model = genai.GenerativeModel('gemini-1.5-flash')
                    chat_response = chat_model.generate_content(f"Context: {report}\n\nUser Question: {user_question}\nAnswer:")
                    st.write(chat_response.text)
            else:
                st.error("⚠️ Google API Key missing in Secrets!")

if __name__ == "__main__":
    main()

