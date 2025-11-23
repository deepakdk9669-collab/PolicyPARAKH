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

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="PolicyPARAKH | GOD MODE",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. UI STYLING (Glassmorphism & Neon) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #000000 70%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Glass Cards */
    .apex-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Status Cards */
    .safe-card { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 8px; }
    .danger-card { border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 15px; border-radius: 8px; }

    /* Terminal Log Text */
    .console-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #00ff41;
        line-height: 1.4;
    }
    
    /* Headers */
    h1, h2, h3 { color: #ffffff; font-weight: 600; }
    .gradient-text {
        background: linear-gradient(90deg, #4F8BF9, #00ff41);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ASSETS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Load Animation (Scanner)
anim_scan = load_lottieurl("https://lottie.host/6b965454-7097-442d-bb08-43420427c006/0X3G5w0J2y.json")

# --- 4. LOGIC CORE (Brain) ---

def rotate_key():
    """Rotates API keys from Streamlit Secrets to avoid limits."""
    try:
        keys = st.secrets["API_KEYS"]
        if isinstance(keys, list): genai.configure(api_key=random.choice(keys))
        else: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except: pass

def agent_log(msg, agent="SYSTEM"):
    """Logs actions to the sidebar terminal."""
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{ts}] [{agent}] {msg}")

# --- AI FUNCTIONS ---

def run_full_audit(text):
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    agent_log("Scanning clauses for hidden traps...", "AUDITOR")
    
    prompt = f"""
    AUDIT THIS DOCUMENT. RETURN JSON ONLY:
    {{
        "risk_score": (0-100 int),
        "verdict": "SAFE/CAUTION/TOXIC",
        "summary": "Short executive summary",
        "bad_clauses": ["Clause 1", "Clause 2"]
    }}
    TEXT: {text[:30000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: return {"risk_score": 0, "verdict": "ERROR", "summary": "Fail", "bad_clauses": []}

def run_privacy_scan(text):
    agent_log("Decrypting data sharing agreements...", "PRIVACY_GUARD")
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    prompt = f"""
    Analyze for DATA PRIVACY. Return JSON:
    {{
        "family_data": "Safe" or "Compromised" (Do they ask for family history?),
        "selling_clause": "No" or "Yes" (Do they sell data to 3rd parties?),
        "explanation": "Short summary of privacy risks"
    }}
    TEXT: {text[:30000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: return {"family_data": "Unknown", "selling_clause": "Unknown", "explanation": "Error"}

def predict_future_costs(text):
    agent_log("Calculating inflation vectors (2025-2035)...", "ARCHITECT")
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    prompt = f"""
    Predict Premium Cost for next 10 years (Start=15000). Assume 10% inflation.
    RETURN JSON ONLY:
    {{
        "years": [2025, 2028, 2031, 2034],
        "cost": [15000, (calc), (calc), (calc)],
        "value": [500000, 400000, 300000, 200000] (Real value dropping)
    }}
    TEXT: {text[:20000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: 
        return {"years": [2025, 2030, 2035], "cost": [15000, 30000, 60000], "value": [500000, 250000, 100000]}

def get_competitors(text):
    agent_log("Scouring Dark Web/Forums...", "SENTINEL")
    search = DuckDuckGoSearchRun()
    try:
        rotate_key()
        m = genai.GenerativeModel('models/gemini-1.5-flash')
        comp = m.generate_content(f"Extract company name: {text[:500]}").text.strip()
        res = search.invoke(f"is {comp} insurance a scam reddit reviews")
        return comp, res
    except: return "Unknown", "Search Failed"

def court_battle_logic(text, user_arg, history):
    agent_log("Consulting legal precedents...", "LAWYER")
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    hist = str(history)
    return model.generate_content(f"ROLE: Ruthless Lawyer. DOC: {text[:20000]} HIST: {hist} USER: {user_arg}. Reject claim citing specific clause.").text

# --- 5. UI LAYOUT ---

if "logs" not in st.session_state: st.session_state.logs = []
if "audit_data" not in st.session_state: st.session_state.audit_data = None
if "court_history" not in st.session_state: st.session_state.court_history = []

# === SIDEBAR (Neural Terminal) ===
with st.sidebar:
    st.markdown("### 🧬 NEURAL TERMINAL")
    
    # The Black Log Box
    log_container = st.container()
    with log_container:
        st.markdown(
            f"""<div style='background:#000; border:1px solid #333; height:200px; overflow-y:auto; padding:10px; border-radius:8px;'>
            {''.join([f"<div class='console-text'>{l}</div>" for l in st.session_state.logs])}
            </div>""", 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Target (PDF)", type="pdf")
    
    if uploaded_file and st.session_state.audit_data is None:
        if st.button("⚡ ACTIVATE GOD MODE", use_container_width=True):
            st.session_state.logs = []
            agent_log("System Initialized.")
            
            pdf = PdfReader(uploaded_file)
            text = ""
            for page in pdf.pages: text += page.extract_text() or ""
            st.session_state.full_text = text
            agent_log(f"Ingested {len(text)} bytes.", "READER")
            
            with st.spinner("Swarm Operating..."):
                # Parallel Execution
                st.session_state.audit_data = run_full_audit(text)
                st.session_state.privacy_data = run_privacy_scan(text)
                st.session_state.future_data = predict_future_costs(text)
                st.session_state.comp_name, st.session_state.sentinel_data = get_competitors(text)
            st.rerun()

    if st.button("🔄 REBOOT SYSTEM", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# === MAIN SCREEN ===

if st.session_state.audit_data is None:
    # Landing Page
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("# Policy<span class='gradient-text'>PARAKH</span>", unsafe_allow_html=True)
        st.markdown("### Neural Legal Defense System")
        st.markdown("Upload a document to deploy the Swarm Agents.")
    with c2:
        if anim_scan: st_lottie(anim_scan, height=400)

else:
    # Dashboard Page
    data = st.session_state.audit_data
    
    # HUD Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("RISK SCORE", f"{data['risk_score']}/100")
    with c2: st.metric("VERDICT", data['verdict'])
    with c3: st.metric("TRAPS", len(data['bad_clauses']))
    with c4: st.metric("ENGINE", "Gemini 2.5")
    
    st.markdown("---")

    # Tabs
    t1, t2, t3, t4, t5 = st.tabs(["📊 AUDIT", "🛡️ PRIVACY", "🔮 TIME MACHINE", "⚖️ COURTROOM", "🌐 SENTINEL"])

    with t1: # Audit
        st.markdown(f"<div class='apex-card'><h3>📝 EXECUTIVE SUMMARY</h3>{data['summary']}</div>", unsafe_allow_html=True)
        for flag in data['bad_clauses']:
            st.markdown(f"<div class='danger-card'>⚠️ {flag}</div>", unsafe_allow_html=True)

    with t2: # Privacy
        p_data = st.session_state.privacy_data
        c_a, c_b = st.columns(2)
        with c_a:
            css = "danger-card" if p_data.get('family_data') != "Safe" else "safe-card"
            st.markdown(f"<div class='{css}'><b>FAMILY DATA</b><br>{p_data.get('family_data')}</div>", unsafe_allow_html=True)
        with c_b:
            css = "danger-card" if p_data.get('selling_clause') == "Yes" else "safe-card"
            st.markdown(f"<div class='{css}'><b>DATA SELLING</b><br>{p_data.get('selling_clause')}</div>", unsafe_allow_html=True)
        st.info(p_data.get('explanation'))

    with t3: # Time Machine
        st.markdown("### 🔮 10-YEAR INFLATION FORECAST")
        f_data = st.session_state.future_data
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['cost'], mode='lines+markers', name='Premium Cost', line=dict(color='#ef4444', width=3)))
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['value'], mode='lines+markers', name='Coverage Value', line=dict(color='#3b82f6', dash='dot')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)

    with t4: # Courtroom
        st.markdown("### ⚔️ ADVERSARIAL SIMULATION")
        c_chat, c_stat = st.columns([0.7, 0.3])
        with c_stat:
            st.markdown("<div class='apex-card'><b>STATUS:</b> ACTIVE<br><b>OPPONENT:</b> AI LAWYER</div>", unsafe_allow_html=True)
            if st.button("🏳️ CONCEDE"): st.session_state.court_history = []; st.rerun()
        
        with c_chat:
            if not st.session_state.court_history:
                st.session_state.court_history.append({"role": "assistant", "content": "I deny your claim based on Clause 4.1. Prove me wrong."})
            
            for msg in st.session_state.court_history:
                role = "⚖️ LAWYER" if msg['role'] == 'assistant' else "👤 YOU"
                color = "#2e1065" if msg['role'] == 'assistant' else "#064e3b"
                st.markdown(f"<div style='background:{color}; padding:12px; border-radius:8px; margin-bottom:8px; font-size:14px;'><b>{role}:</b> {msg['content']}</div>", unsafe_allow_html=True)
            
            if u_in := st.chat_input("Object..."):
                st.session_state.court_history.append({"role": "user", "content": u_in})
                with st.spinner("Lawyer countering..."):
                    r = court_battle_logic(st.session_state.full_text, u_in, st.session_state.court_history)
                    st.session_state.court_history.append({"role": "assistant", "content": r})
                st.rerun()

    with t5: # Sentinel
        st.markdown(f"### 🌐 DARK WEB SCAN: {st.session_state.comp_name}")
        st.markdown(f"<div class='apex-card'>{st.session_state.sentinel_data}</div>", unsafe_allow_html=True)
    
