import streamlit as st
import time
import random
import json
import re
from PyPDF2 import PdfReader
import google.generativeai as genai
from duckduckgo_search import DDGS
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="PolicyPARAKH",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. UI STYLING (Clean Dark Mode) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    
    /* Cards */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #262730; border-radius: 10px; padding: 15px; border: 1px solid #333;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #1F2937; border-left: 4px solid #3B82F6; padding: 10px; border-radius: 5px;
    }
    
    /* Chat Bubbles */
    .lawyer-msg { background-color: #450a0a; color: #fecaca; padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 3px solid red; }
    .user-msg { background-color: #064e3b; color: #a7f3d0; padding: 10px; border-radius: 10px; margin-bottom: 5px; text-align: right; border-right: 3px solid green; }
    
    /* Buttons */
    .stButton>button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ASSETS ---
def load_lottieurl(url):
    try: return requests.get(url).json()
    except: return None

anim_scan = load_lottieurl("https://lottie.host/6b965454-7097-442d-bb08-43420427c006/0X3G5w0J2y.json")

# --- 4. LOGIC CORE (The Universal Brain) ---

def rotate_key():
    """Rotates keys to avoid limits"""
    try:
        keys = st.secrets["API_KEYS"]
        if isinstance(keys, list): genai.configure(api_key=random.choice(keys))
        else: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except: pass

def sentinel_search(query):
    """Real-time Scam Check"""
    try:
        results = DDGS().text(f"{query} insurance complaints scam reddit", max_results=3)
        return "\n".join([f"- {r['body'][:150]}..." for r in results]) if results else "No negative reports found."
    except: return "Sentinel Network Offline."

# --- UNIVERSAL AUDIT LOGIC ---
def run_universal_audit(text):
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # This prompt combines the "Genesis" Universal Logic with "God Mode" output
    prompt = f"""
    ROLE: PolicyPARAKH v1 (Universal Auditor).
    
    STEP 1: CLASSIFY DOC TYPE (Health, Motor, Life, or Contract).
    
    STEP 2: AUDIT BASED ON TYPE:
    - Health: Check Room Rent Limit, Co-pay, Diseases.
    - Motor: Check IDV, Zero-Dep, Engine Cover.
    - Life: Check Suicide Clause, Claim Ratio.
    - Contract: Check Data Privacy, Auto-Renewal.
    
    OUTPUT JSON ONLY:
    {{
        "doc_type": "Detected Type",
        "risk_score": (0-100 int),
        "verdict": "SAFE / CAUTION / TOXIC",
        "summary": "2 line professional summary",
        "red_flags": ["Clause 1 details", "Clause 2 details", "Clause 3 details"],
        "privacy_alert": "Yes/No (Is data being sold?)",
        "good_points": ["Feature 1", "Feature 2"]
    }}
    DOC TEXT: {text[:30000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: return {"doc_type": "Unknown", "risk_score": 0, "verdict": "ERROR", "summary": "Audit Failed", "red_flags": []}

# --- TIME MACHINE LOGIC ---
def get_inflation_data(text):
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    prompt = f"""
    Analyze 'Age Banding' & 'Inflation' in this text. Predict Premium for next 10 years (Start=15000).
    RETURN JSON: {{ "years": [2025, 2028, 2031, 2034], "cost": [15000, int, int, int], "value": [500000, int, int, int] }}
    TEXT: {text[:10000]}
    """
    try:
        res = model.generate_content(prompt).text
        return json.loads(re.search(r"\{.*\}", res, re.DOTALL).group(0))
    except: return {"years": [2025, 2030, 2035], "cost": [15000, 30000, 60000], "value": [500000, 250000, 100000]}

# --- COURTROOM LOGIC ---
def court_logic(text, user_arg, history):
    rotate_key()
    model = genai.GenerativeModel('models/gemini-1.5-pro') # Using Pro for better argument
    hist = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    return model.generate_content(f"ROLE: Ruthless Insurance Lawyer. DOC: {text[:20000]} HIST: {hist} USER: {user_arg}. Reject claim citing clause.").text

# --- 5. UI LAYOUT ---

if "audit_data" not in st.session_state: st.session_state.audit_data = None
if "court_history" not in st.session_state: st.session_state.court_history = []

# SIDEBAR
with st.sidebar:
    st.title("🛡️ PolicyPARAKH")
    st.caption("v1: Universal Edition")
    
    uploaded_file = st.file_uploader("Upload Document", type="pdf")
    
    if uploaded_file and st.session_state.audit_data is None:
        if st.button("🚀 Start Universal Audit"):
            with st.status("⚙️ Swarm Active...", expanded=True):
                st.write("📂 Reading Document...")
                pdf = PdfReader(uploaded_file)
                text = ""
                for page in pdf.pages: text += page.extract_text() or ""
                st.session_state.full_text = text
                
                st.write("🧠 Classifying & Analyzing...")
                st.session_state.audit_data = run_universal_audit(text)
                
                st.write("🌐 Sentinel Scanning...")
                # Quick company extract for search
                try: 
                    rotate_key()
                    comp = genai.GenerativeModel('models/gemini-1.5-flash').generate_content(f"Extract company name: {text[:500]}").text.strip()
                except: comp = "Insurance Company"
                st.session_state.comp_name = comp
                st.session_state.sentinel_data = sentinel_search(comp)
                
                st.write("🔮 Calculating Future...")
                st.session_state.time_data = get_inflation_data(text)
                
            st.rerun()

    if st.button("🔄 New Scan"):
        st.session_state.clear()
        st.rerun()

# MAIN DASHBOARD
if st.session_state.audit_data is None:
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        st.title("PolicyPARAKH v1")
        st.markdown("### The Universal Legal Auditor.")
        st.info("👈 Upload any Policy (Health, Motor, Life) to begin.")
    with c2:
        if anim_scan: st_lottie(anim_scan, height=300)

else:
    data = st.session_state.audit_data
    
    # HUD Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Doc Type", data.get('doc_type', 'Unknown'))
    with c2: st.metric("Risk Score", f"{data['risk_score']}/100")
    with c3: st.metric("Verdict", data['verdict'])
    with c4: st.metric("Privacy Risk", data.get('privacy_alert', 'Unknown'))
    
    st.divider()
    
    # TABS (Combining all features)
    t1, t2, t3, t4 = st.tabs(["📝 Audit Report", "🔮 Time Machine", "⚖️ Courtroom", "🌐 Sentinel"])
    
    with t1:
        st.subheader("Executive Summary")
        st.write(data['summary'])
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.error("🚩 **Critical Red Flags**")
            for flag in data['red_flags']: st.write(f"• {flag}")
        with c_b:
            st.success("✅ **Good Points**")
            for good in data.get('good_points', []): st.write(f"• {good}")

    with t2:
        st.subheader("📉 Financial Forecast (10 Years)")
        f_data = st.session_state.time_data
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['cost'], name='Premium Cost (Rising)', line=dict(color='#EF4444', width=4)))
        fig.add_trace(go.Scatter(x=f_data['years'], y=f_data['value'], name='Real Value (Falling)', line=dict(color='#3B82F6', dash='dot')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.subheader("⚖️ Simulation: Fight the Lawyer")
        if not st.session_state.court_history:
            st.session_state.court_history.append({"role": "assistant", "content": "I deny your claim based on the exclusion clause. Prove me wrong."})
        
        for msg in st.session_state.court_history:
            css = "lawyer-msg" if msg['role'] == 'assistant' else "user-msg"
            role = "⚖️ LAWYER" if msg['role'] == 'assistant' else "👤 YOU"
            st.markdown(f"<div class='{css}'><b>{role}:</b> {msg['content']}</div>", unsafe_allow_html=True)
        
        if prompt := st.chat_input("Object here..."):
            st.session_state.court_history.append({"role": "user", "content": prompt})
            with st.spinner("Lawyer objecting..."):
                resp = court_logic(st.session_state.full_text, prompt, st.session_state.court_history)
                st.session_state.court_history.append({"role": "assistant", "content": resp})
            st.rerun()

    with t4:
        st.subheader(f"🌐 Market Intelligence: {st.session_state.comp_name}")
        st.info("Real-time data from Reddit & Consumer Forums via DuckDuckGo.")
        st.markdown(st.session_state.sentinel_data)
        
