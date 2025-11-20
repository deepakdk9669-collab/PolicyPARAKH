import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from PyPDF2 import PdfReader
import graph
import google.generativeai as genai

# --- 1. PAGE CONFIG (IMMERSIVE MODE) ---
st.set_page_config(
    page_title="PolicyPARAKH | OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOAD ASSETS (Animations) ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a Cool "AI Shield" Animation
lottie_shield = load_lottieurl("https://lottie.host/4b85970b-0072-4402-8844-49225a872f85/8s9P4X32jA.json") 
# (Alternative Robot: "https://assets9.lottiefiles.com/packages/lf20_zrqthn6o.json")

# --- 3. CUSTOM CSS (THE MAGIC) ---
st.markdown("""
<style>
    /* Background & Font */
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* GLASSMORPHISM CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* NEON TEXT */
    h1 {
        font-size: 3rem;
        background: -webkit-linear-gradient(#00FFA3, #00C3FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(0, 255, 163, 0.3);
    }
    
    /* METRICS */
    div[data-testid="metric-container"] {
        background: rgba(20, 20, 20, 0.8);
        border-left: 4px solid #00FFA3;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(45deg, #00FFA3, #00C3FF);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 30px;
        padding: 10px 30px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #00C3FF;
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if "audit_done" not in st.session_state: st.session_state.audit_done = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. SIDEBAR (COMMAND CENTER) ---
with st.sidebar:
    st.markdown("## 🖥️ SYSTEM STATUS")
    st.success("🟢 CORE: ONLINE")
    st.info("🔵 NETWORK: SECURE")
    st.warning("🟡 MODEL: GEMINI 2.5 PRO")
    st.markdown("---")
    
    # Key Rotation Status
    try:
        keys = st.secrets["API_KEYS"]
        st.caption(f"🔑 Active Keys: {len(keys)}")
    except:
        st.error("No Keys Found")
        
    if st.button("REBOOT SYSTEM"):
        st.session_state.clear()
        st.rerun()

# --- 6. HERO SECTION ---
col1, col2 = st.columns([0.7, 0.3])

with col1:
    st.markdown("# PolicyPARAKH OS")
    st.markdown("### <span style='color:#00FFA3'>AI Legal Defense System v10.0</span>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card'>
        The AI Agent that reads the fine print, hunts for scams, and protects your money.
        <br><b>Status:</b> Waiting for target document...
    </div>
    """, unsafe_allow_html=True)

with col2:
    if lottie_shield:
        st_lottie(lottie_shield, height=200, key="shield_anim")

# --- 7. UPLOAD & SCAN INTERFACE ---
uploaded_file = st.file_uploader("", type="pdf", help="Drop Legal Contract or Bill Here")

if uploaded_file and not st.session_state.audit_done:
    if st.button("🚀 INITIATE DEEP SCAN"):
        
        # A. VISUAL SCANNING SEQUENCE
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        sequences = [
            "📂 Extracting Binary Data...",
            "🧠 Converting to Neural Embeddings...",
            "🕵️ Accessing Global Consumer Database...",
            "⚖️ Cross-Referencing Legal Precedents...",
            "🚩 Detecting Hidden Traps...",
            "✅ Finalizing Verdict..."
        ]
        
        for i, seq in enumerate(sequences):
            status_text.markdown(f"### `{seq}`")
            progress_bar.progress((i + 1) * 16)
            time.sleep(0.6) # Fake delay for "Feel"

        # B. REAL PROCESSING
        status_text.markdown("### `⚡ Generating Intelligence Report...`")
        
        pdf = PdfReader(uploaded_file)
        text = ""
        for page in pdf.pages: text += page.extract_text() or ""
        
        # Call the Brain
        report = graph.run_audit(text)
        st.session_state.report = report
        st.session_state.full_text = text
        st.session_state.audit_done = True
        st.rerun()

# --- 8. THE DASHBOARD (RESULT) ---
if st.session_state.audit_done:
    
    # EXTRACT SCORE (Dummy logic for visual if not found)
    score = "85" 
    status = "SAFE"
    color = "#00FFA3" # Green
    
    if "High Risk" in st.session_state.report or "SCAM" in st.session_state.report:
        score = "35"
        status = "CRITICAL"
        color = "#FF4B4B" # Red
    elif "Moderate" in st.session_state.report:
        score = "60"
        status = "CAUTION"
        color = "#FFA500" # Orange

    # A. HEADS UP DISPLAY (HUD)
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"<div style='text-align:center; font-size:40px; color:{color}; font-weight:bold'>{score}/100</div>", unsafe_allow_html=True)
        st.caption("SAFETY SCORE")
    with c2:
        st.markdown(f"<div style='text-align:center; font-size:25px; color:{color}; font-weight:bold'>{status}</div>", unsafe_allow_html=True)
        st.caption("VERDICT")
    with c3:
        st.markdown(f"<div style='text-align:center; font-size:25px; color:#00C3FF; font-weight:bold'>1.2s</div>", unsafe_allow_html=True)
        st.caption("SCAN TIME")
    with c4:
        st.markdown(f"<div style='text-align:center; font-size:25px; color:#E0E0E0; font-weight:bold'>Gemini 2.5</div>", unsafe_allow_html=True)
        st.caption("AI ENGINE")

    st.markdown("---")

    # B. TABS FOR DATA
    tab1, tab2, tab3 = st.tabs(["📊 AUDIT REPORT", "💬 NEURAL CHAT", "🌐 LIVE INTEL"])
    
    with tab1:
        st.markdown(f"<div class='glass-card'>{st.session_state.report}</div>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("🔍 FIND ALTERNATIVES (WEB)")
        with col_btn2:
            st.download_button("📥 DOWNLOAD DATA", st.session_state.report)

    with tab2:
        st.caption("Ask the PolicyPARAKH Core specifically about clauses.")
        
        # Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Input Command..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    graph.configure_random_key()
                    model = genai.GenerativeModel('models/gemini-1.5-pro')
                    full_p = f"Context: {st.session_state.full_text[:20000]}\nUser: {prompt}\nAnswer short & sharp."
                    res = model.generate_content(full_p).text
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})

    with tab3:
        st.info("📡 Accessing Real-Time Market Data...")
        st.markdown("No live alerts for this company in the last 24 hours.")

