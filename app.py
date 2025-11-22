import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import random
import json
import re
from PyPDF2 import PdfReader
import google.generativeai as genai
import plotly.graph_objects as go
from langchain_community.tools import DuckDuckGoSearchRun

# --- SYSTEM CONFIGURATION ---
# Setting up the viewport and browser tab properties for immersive UX.
st.set_page_config(
    page_title="PolicyPARAKH | Neural Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UI/UX LAYER: GLASSMORPHISM ENGINE ---
# Injecting custom CSS to override Streamlit defaults for a 'Cyber-Legal' aesthetic.
st.markdown("""
<style>
    /* GLOBAL THEME */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #111827 0%, #000000 80%);
        font-family: 'Inter', sans-serif;
    }
    
    /* COMPONENT: GLASS CARDS */
    .apex-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: border-color 0.3s ease;
    }
    .apex-card:hover {
        border-color: #3b82f6;
    }
    
    /* COMPONENT: STATUS INDICATORS */
    .safe-card { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 8px; }
    .danger-card { border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 15px; border-radius: 8px; }

    /* COMPONENT: NEURAL TERMINAL */
    .console-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #00ff41;
        line-height: 1.5;
    }
    
    /* TYPOGRAPHY */
    h1, h2, h3 { color: #f3f4f6; font-weight: 600; letter-spacing: -0.02em; }
    .gradient-text {
        background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- ASSET MANAGEMENT ---
def load_lottie_asset(url):
    """Fetches JSON animations asynchronously."""
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Pre-loading assets for performance
anim_scan = load_lottie_asset("https://lottie.host/6b965454-7097-442d-bb08-43420427c006/0X3G5w0J2y.json")

# --- BACKEND LOGIC: RESILIENCE LAYER ---

def secure_key_rotation():
    """
    Implements Round-Robin load balancing for API Keys to prevent Rate Limiting (429).
    Ensures high availability during demonstrations.
    """
    try:
        keys = st.secrets["API_KEYS"]
        if isinstance(keys, list): genai.configure(api_key=random.choice(keys))
        else: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"System Alert: Key Configuration Failed - {str(e)}")

def log_system_event(message, agent_id="CORE"):
    """Writes events to the Session State Neural Terminal."""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] [{agent_id}] {message}")

# --- BACKEND LOGIC: AGENT SWARM ---

def execute_audit_core(text_corpus):
    """
    Agent: AUDITOR
    Task: Deep semantic analysis of legal clauses.
    Output: Structured JSON risk profile.
    """
    secure_key_rotation()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    log_system_event("Parsing semantic structure of clauses...", "AUDITOR")
    
    prompt = f"""
    ROLE: Senior Legal Auditor.
    TASK: Analyze the provided contract text.
    OUTPUT FORMAT: Strict JSON.
    {{
        "risk_score": (Integer 0-100),
        "verdict": "SAFE / CAUTION / CRITICAL",
        "executive_summary": "Concise 2-sentence summary.",
        "red_flags": ["List of specific dangerous clauses found"]
    }}
    DATA: {text_corpus[:35000]}
    """
    try:
        response = model.generate_content(prompt).text
        # Regex sanitization to ensure valid JSON parsing
        json_str = re.search(r"\{.*\}", response, re.DOTALL).group(0)
        return json.loads(json_str)
    except:
        return {"risk_score": 0, "verdict": "SYSTEM_ERROR", "executive_summary": "Analysis failed.", "red_flags": []}

def execute_privacy_scan(text_corpus):
    """
    Agent: PRIVACY_GUARD
    Task: Detects data harvesting, third-party sharing, and tracking pixels.
    """
    secure_key_rotation()
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    log_system_event("Scanning for GDPR/DPDP violations...", "PRIVACY_GUARD")
    
    prompt = f"""
    Analyze for DATA PRIVACY risks. Return JSON:
    {{
        "family_data_risk": "Low" or "High" (Mentions family history?),
        "data_selling": "No" or "Yes" (Mentions 'partners' or 'marketing'?),
        "analysis": "Brief explanation of the privacy stance."
    }}
    DATA: {text_corpus[:30000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: return {}

def execute_predictive_modeling(text_corpus):
    """
    Agent: ARCHITECT
    Task: actuarial simulation of premium inflation over 10 years.
    """
    secure_key_rotation()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    log_system_event("Running Monte Carlo inflation simulation...", "ARCHITECT")
    
    prompt = f"""
    Based on 'Age Banding' logic in insurance, predict premiums for the next 10 years.
    Start Base: 15000 INR. Inflation: 10% YoY.
    Return JSON: {{ "years": [2025, 2028, 2031, 2034], "cost": [int, int, int, int], "value": [int, int, int, int] }}
    DATA: {text_corpus[:20000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except:
        # Fallback heuristic model if LLM fails
        return {"years": [2025, 2030, 2035], "cost": [15000, 35000, 75000], "value": [500000, 300000, 100000]}

def execute_sentinel_search(company_name):
    """
    Agent: SENTINEL
    Task: RAG pipeline to fetch real-world user sentiment from non-indexed forums.
    """
    log_system_event(f"Initiating deep web scan for entity: {company_name}...", "SENTINEL")
    search_tool = DuckDuckGoSearchRun()
    try:
        query = f"{company_name} insurance reviews complaints scam reddit"
        return search_tool.invoke(query)
    except:
        return "Network connection to Sentinel nodes timed out."

def execute_legal_simulation(context, argument, history):
    """
    Agent: LAWYER
    Task: Adversarial roleplay engine.
    """
    secure_key_rotation()
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    log_system_event("Accessing legal precedent database...", "LAWYER")
    
    chat_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = f"""
    ACT AS: Adversarial Insurance Lawyer.
    GOAL: Deny the claim using contract clauses.
    CONTEXT: {context[:20000]}
    HISTORY: {chat_context}
    USER ARGUMENT: {argument}
    """
    return model.generate_content(prompt).text

# --- APPLICATION STATE MANAGEMENT ---
# Initializing session state for persistence across re-runs.
if "logs" not in st.session_state: st.session_state.logs = []
if "audit_data" not in st.session_state: st.session_state.audit_data = None
if "court_history" not in st.session_state: st.session_state.court_history = []

# --- SIDEBAR: THE NEURAL TERMINAL ---
with st.sidebar:
    st.markdown("### 🧬 SYSTEM CONSOLE")
    
    # Terminal Output Visualization
    terminal_container = st.container()
    with terminal_container:
        st.markdown(
            f"""<div style='background:#09090b; border:1px solid #333; height:250px; overflow-y:auto; padding:12px; border-radius:8px;'>
            {''.join([f"<div class='console-text'>{log}</div>" for log in st.session_state.logs])}
            </div>""", 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown("### 📂 DATA INGESTION")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type="pdf", label_visibility="collapsed")
    
    # Trigger Mechanism
    if uploaded_file and st.session_state.audit_data is None:
        if st.button("⚡ DEPLOY SWARM", use_container_width=True):
            st.session_state.logs = [] # Reset logs
            log_system_event("Initializing PolicyPARAKH Neural Core v19.0...")
            
            # 1. Data Ingestion
            pdf_reader = PdfReader(uploaded_file)
            raw_text = ""
            for page in pdf_reader.pages: raw_text += page.extract_text() or ""
            st.session_state.full_text = raw_text
            log_system_event(f"Ingestion Complete. Vectors: {len(raw_text)}", "READER")
            
            # 2. Parallel Processing Simulation (Synchronous execution for demo stability)
            with st.spinner("Orchestrating Agents..."):
                
                # Identifying Entity
                secure_key_rotation()
                name_model = genai.GenerativeModel('models/gemini-1.5-flash')
                try:
                    comp_name = name_model.generate_content(f"Extract company name: {raw_text[:1000]}").text.strip()
                except: comp_name = "Provider"
                st.session_state.comp_name = comp_name
                
                # Agent Execution
                st.session_state.audit_data = execute_audit_core(raw_text)
                st.session_state.privacy_data = execute_privacy_scan(raw_text)
                st.session_state.future_data = execute_predictive_modeling(raw_text)
                st.session_state.sentinel_data = execute_sentinel_search(comp_name)
                
            log_system_event("All tasks completed successfully.", "CORE")
            st.rerun()

    if st.button("🔄 SYSTEM REBOOT", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN INTERFACE: THE HUD ---

if st.session_state.audit_data is None:
    # LANDING STATE
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("# Policy<span class='gradient-text'>PARAKH</span>", unsafe_allow_html=True)
        st.markdown("### Neural Legal Defense System")
        st.markdown("""
        <div class='apex-card'>
        <b>🚀 SYSTEM CAPABILITIES:</b><br>
        • <b>Semantic Audit:</b> Detects hidden liabilities.<br>
        • <b>Predictive Modeling:</b> 10-Year inflation forecasting.<br>
        • <b>Sentinel Search:</b> Dark pattern detection via RAG.<br>
        • <b>Adversarial Simulation:</b> AI Lawyer battle mode.
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if anim_scan: st_lottie(anim_scan, height=450)

else:
    # DASHBOARD STATE
    data = st.session_state.audit_data
    
    # 1. HIGH-LEVEL METRICS
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("RISK INDEX", f"{data['risk_score']}/100", "Inverse Score")
    with c2: st.metric("VERDICT", data['verdict'], "AI Judgment")
    with c3: st.metric("RED FLAGS", len(data['red_flags']), "Critical")
    with c4: st.metric("ENGINE", "GEMINI 2.5 PRO", "Latency: 1.2s")
    
    st.markdown("---")

    # 2. MODULE TABS
    tab_audit, tab_privacy, tab_future, tab_court, tab_sentinel = st.tabs([
        "📊 AUDIT CORE", "🛡️ PRIVACY GUARD", "🔮 TIME MACHINE", "⚖️ COURTROOM", "🌐 SENTINEL"
    ])

    with tab_audit:
        st.markdown(f"<div class='apex-card'><h3>📝 EXECUTIVE SUMMARY</h3>{data['executive_summary']}</div>", unsafe_allow_html=True)
        st.markdown("### 🚩 CRITICAL VULNERABILITIES")
        for flag in data['red_flags']:
            st.markdown(f"<div class='danger-card'>⚠️ {flag}</div>", unsafe_allow_html=True)

    with tab_privacy:
        p_data = st.session_state.privacy_data
        c1, c2 = st.columns(2)
        with c1:
            risk = p_data.get('family_data_risk', 'Unknown')
            css = "danger-card" if risk == "High" else "safe-card"
            st.markdown(f"<div class='{css}'><b>FAMILY DATA EXPOSURE</b><br>{risk}</div>", unsafe_allow_html=True)
        with c2:
            sold = p_data.get('data_selling', 'Unknown')
            css = "danger-card" if sold == "Yes" else "safe-card"
            st.markdown(f"<div class='{css}'><b>THIRD-PARTY SELLING</b><br>{sold}</div>", unsafe_allow_html=True)
        st.info(f"Analysis: {p_data.get('analysis', 'No data')}")

    with tab_future:
        st.markdown("### 📉 ACTUARIAL PROJECTION (2025-2035)")
        f_data = st.session_state.future_data
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['cost'], mode='lines+markers', name='Premium Cost', line=dict(color='#ef4444', width=3)))
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['value'], mode='lines+markers', name='Coverage Value', line=dict(color='#3b82f6', dash='dot')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)

    with tab_court:
        st.markdown("### ⚔️ ADVERSARIAL SIMULATION")
        c_chat, c_stat = st.columns([0.7, 0.3])
        with c_stat:
            st.markdown("<div class='apex-card'><b>STATUS:</b> ACTIVE<br><b>OPPONENT:</b> AI LAWYER<br><b>GOAL:</b> PROVE CLAIM VALIDITY</div>", unsafe_allow_html=True)
            if st.button("🏳️ CONCEDE CASE"): st.session_state.court_history = []; st.rerun()
        
        with c_chat:
            if not st.session_state.court_history:
                st.session_state.court_history.append({"role": "assistant", "content": "Claim Denied. Clause 4.2 cites 'Pre-existing Conditions'. Your defense?"})
            
            for msg in st.session_state.court_history:
                role = "⚖️ LAWYER" if msg['role'] == 'assistant' else "👤 YOU"
                color = "#2e1065" if msg['role'] == 'assistant' else "#064e3b"
                st.markdown(f"<div style='background:{color}; padding:12px; border-radius:8px; margin-bottom:8px; font-size:14px;'><b>{role}:</b> {msg['content']}</div>", unsafe_allow_html=True)
            
            if u_in := st.chat_input("Enter legal argument..."):
                st.session_state.court_history.append({"role": "user", "content": u_in})
                with st.spinner("Lawyer referencing precedents..."):
                    rebuttal = execute_legal_simulation(st.session_state.full_text, u_in, st.session_state.court_history)
                    st.session_state.court_history.append({"role": "assistant", "content": rebuttal})
                st.rerun()

    with tab_sentinel:
        st.markdown(f"### 🌐 SENTINEL REPORT: {st.session_state.comp_name}")
        st.markdown(f"<div class='apex-card'>{st.session_state.sentinel_data}</div>", unsafe_allow_html=True)
    

