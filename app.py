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

# Config
st.set_page_config(page_title="PolicyPARAKH AI", layout="wide", initial_sidebar_state="expanded")

# Gemini-Inspired CSS (The Real Deal)
st.markdown("""
<style>
    /* Main Background - Pure Dark */
    .stApp { background-color: #131314; color: #E3E3E3; font-family: 'Google Sans', sans-serif; }
    
    /* Sidebar - Slightly Lighter Dark */
    [data-testid="stSidebar"] { background-color: #1E1F20; border-right: 1px solid #333; }
    
    /* Floating Chat Input (Gemini Style) */
    .stChatInput { 
        position: fixed; 
        bottom: 20px; 
        left: 50%; 
        transform: translateX(-50%); 
        width: 60%; 
        z-index: 1000; 
        background-color: #1E1F20; 
        border-radius: 25px; 
        border: 1px solid #444; 
    }
    
    /* Gem Button Styling */
    .gem-btn {
        display: block; 
        width: 100%; 
        padding: 12px; 
        margin: 5px 0; 
        background: #28292A; 
        color: white; 
        border-radius: 12px; 
        text-align: left; 
        border: none; 
        transition: 0.3s;
        font-weight: 500;
    }
    .gem-btn:hover { background: #3C4043; color: #8AB4F8; cursor: pointer; }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    @media (max-width: 768px) { .stChatInput { width: 95%; left: 2.5%; transform: none; } }
</style>
""", unsafe_allow_html=True)

# State Initialization
if "page" not in st.session_state: st.session_state.page = "home"
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

# Helper Functions
def navigate(page): st.session_state.page = page; st.rerun()
def add_msg(role, content): st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")

# Sidebar Navigation
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"): new_chat()
    
    st.markdown("### Gems")
    if st.button("⚖️ Courtroom Simulator", help="Dedicated Simulator"): navigate("courtroom")
    if st.button("🛒 Scout (Tool)", help="Use in Home Chat"): navigate("home")

    st.markdown("### Settings")
    with st.expander("👤 Family Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Mom (Diabetes)")

# PAGE 1: HOME (Chat + Tools)
if st.session_state.page == "home":
    # Only show uploader if no document is active
    if 'auditor_report' not in st.session_state:
        st.markdown("## Hi, I'm PolicyPARAKH. \n### Upload a document or ask me anything.")
        uploaded_file = st.file_uploader("📎 Upload (PDF/Img/Video)", type=["pdf", "png", "jpg", "jpeg", "mp4", "mp3"], label_visibility="collapsed")
    else:
        uploaded_file = None # Hide uploader to keep chat clean like Gemini
    
    client = utils.initialize_gemini()
    
    # Document Processor
    if uploaded_file and client:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing..."):
                ft = uploaded_file.type
                mime = "application/pdf" if "pdf" in ft else (ft if "image" in ft else ("video/mp4" if "video" in ft else "application/pdf"))
                
                if "pdf" in mime:
                    data = utils.base64_encode_pdf(uploaded_file)
                else:
                    import base64
                    data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                report = auditor.generate_risk_assessment(client, "Audit", data, mime)
                if report:
                    st.session_state.auditor_report = report
                    msg = f"✅ **Analysis Complete:** {report.get('summary')}"
                    add_msg("assistant", msg)
                    st.rerun()

    # Chat Display
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Input Area
    audio_val = st.audio_input("🎙️") 
    prompt = st.chat_input("Ask 'Compare', 'Review', or 'Explain'")

    user_input = None
    if audio_val: user_input = "Audio received (Transcription Pending)" 
    elif prompt: user_input = prompt

    if user_input:
        add_msg("user", user_input)
        if audio_val: 
            with st.chat_message("user"): st.markdown(user_input)
        else:
            with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            
            client = utils.initialize_gemini()
            context = st.session_state.get('auditor_report', {})
            prompt_lower = user_input.lower()
            
            # --- TOOL ROUTING ---
            if "compare" in prompt_lower:
                res = market_scout.compare_policy(client, context)
            elif any(x in prompt_lower for x in ["scam", "review", "location"]):
                res = market_scout.get_social_sentiment(client, context.get('entity_name','Company'))
            elif "court" in prompt_lower:
                res = "Please switch to 'Courtroom Mode' from Sidebar."
            else:
                # General Chat with Search
                web = search_engine.search_web(user_input)
                try:
                    res = client.models.generate_content(model='gemini-2.5-pro', contents=f"Context:{context}\nWeb:{web}\nUser:{user_input}").text
                except: res = "Error."
            
            placeholder.markdown(res)
            add_msg("assistant", res)
            if audio_val: st.rerun()

# PAGE 2: COURTROOM (Gem)
elif st.session_state.page == "courtroom":
    st.title("⚖️ Courtroom Simulator")
    if st.button("← Back"): navigate("home")
    
    if claim := st.chat_input("State your claim..."):
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("Fighting..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Policy")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
