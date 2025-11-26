import streamlit as st
import utils
import auditor
import critic
import sentinel
import architect
import courtroom
import market_scout
import search_engine
import uuid
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="PolicyPARAKH AI", layout="wide", initial_sidebar_state="expanded")

# --- GEMINI UI CSS ---
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #E3E3E3; font-family: 'Google Sans', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1E1F20; border-right: 1px solid #333; }
    .stChatInput { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 60%; z-index: 1000; background-color: #1E1F20; border-radius: 25px; border: 1px solid #444; }
    .gem-btn { display: block; width: 100%; padding: 12px; margin: 5px 0; background: #28292A; color: white; border-radius: 12px; text-align: left; border: none; transition: 0.3s; }
    .gem-btn:hover { background: #3C4043; color: #8AB4F8; cursor: pointer; }
    @media (max-width: 768px) { .stChatInput { width: 95%; left: 2.5%; transform: none; } }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "page" not in st.session_state: st.session_state.page = "home"
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

# --- NAVIGATION ---
def navigate(page): st.session_state.page = page; st.rerun()
def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")
def add_msg(role, content): st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

# --- SIDEBAR ---
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"): new_chat()
    
    st.markdown("### Gems")
    if st.button("⚖️ Courtroom Simulator", help="Dedicated Game Mode"): navigate("courtroom")
    if st.button("🛒 Market Scout", help="Comparison Tool"): navigate("home")

    with st.expander("👤 Family Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Mom (Diabetes)")

# --- PAGE 1: HOME ---
if st.session_state.page == "home":
    
    # FEATURE: Universal Uploader (Auto-hides after upload)
    if 'auditor_report' not in st.session_state:
        st.markdown("## Hi, I'm PolicyPARAKH. \n### Upload evidence (PDF/Video/Audio) to start.")
        uploaded_file = st.file_uploader("📎 Upload", type=["pdf", "png", "jpg", "jpeg", "mp4", "mp3"], label_visibility="collapsed")
    else:
        uploaded_file = None

    client = utils.initialize_gemini()
    
    # FEATURE: File Processing
    if uploaded_file and client:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing Evidence..."):
                ft = uploaded_file.type
                mime = "application/pdf" if "pdf" in ft else (ft if "image" in ft else ("video/mp4" if "video" in ft else ("audio/mp3" if "audio" in ft else "application/pdf")))
                
                if "pdf" in mime: data = utils.base64_encode_pdf(uploaded_file)
                else: 
                    import base64
                    data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                report = auditor.generate_risk_assessment(client, "Analyze this.", data, mime)
                if report:
                    st.session_state.auditor_report = report
                    reviewed = critic.review_report(client, report, "Review") # Critic Agent Feature
                    st.session_state.auditor_report = reviewed
                    
                    msg = f"✅ **Evidence Analyzed:** {reviewed.get('summary')}\n\n🚩 **Risks:** {reviewed.get('bad_clauses')}"
                    add_msg("assistant", msg)
                    st.rerun()

    # Chat Interface
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # FEATURE: Voice & Text Input
    audio_val = st.audio_input("🎙️") 
    prompt = st.chat_input("Ask 'Compare', 'Scam check', 'Gwalior hospitals'...")

    user_input = None
    if audio_val: 
        # Transcribe Audio Feature
        user_input = "Audio received (Processing...)" # In full version, send audio to Gemini to transcribe
        # For now, we simulate input. 
        # Ideally: user_input = client.models.generate_content(model='gemini-2.5-flash', contents=[audio_val]).text
    elif prompt: user_input = prompt

    if user_input:
        add_msg("user", user_input)
        # If audio, render user message manually
        if audio_val: 
             with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            
            client = utils.initialize_gemini()
            context = st.session_state.get('auditor_report', {})
            prompt_lower = user_input.lower()
            
            # --- INTELLIGENT TOOL ROUTING ---
            if "compare" in prompt_lower:
                res = market_scout.compare_policy(client, context)
            
            elif "gwalior" in prompt_lower or "location" in prompt_lower:
                res = market_scout.check_local_presence(client, context.get('entity_name','Company'), "Gwalior")
            
            elif any(x in prompt_lower for x in ["scam", "review", "sentiment"]):
                res = market_scout.get_social_sentiment(client, context.get('entity_name','Company'))
            
            elif "court" in prompt_lower:
                res = "Switch to 'Courtroom Simulator' from the Sidebar."
            
            elif "value" in prompt_lower:
                 df = architect.architect_agent_forecast(client, {})
                 st.session_state.architect_data = df
                 res = "Inflation Forecast:"
                 st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])

            else:
                # General Chat + Internet Search
                web = search_engine.search_web(user_input)
                try:
                    res = client.models.generate_content(model='gemini-2.5-pro', contents=f"Context:{context}\nWeb:{web}\nUser:{user_input}").text
                except: res = "Error connecting to brain."
            
            placeholder.markdown(res)
            add_msg("assistant", res)
            if audio_val: st.rerun()

# --- PAGE 2: COURTROOM (Gem) ---
elif st.session_state.page == "courtroom":
    st.markdown("## ⚖️ Virtual Courtroom")
    if st.button("← Back"): navigate("home")
    
    if claim := st.chat_input("State your claim (e.g. Cataract rejected)..."):
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("Researching Case Laws..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Evidence")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
