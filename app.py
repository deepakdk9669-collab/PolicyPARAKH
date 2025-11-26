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

# --- CSS FOR IMMERSIVE UI ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Google Sans', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Chat Input Floating Bar */
    .stChatInput { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 60%; z-index: 1000; background-color: #1E1F20; border-radius: 25px; border: 1px solid #444; }
    
    /* Gem Button Styling */
    .gem-btn {
        display: block; width: 100%; padding: 10px; margin: 5px 0;
        background: #28292A; color: white; border-radius: 10px;
        text-align: left; border: 1px solid #333; transition: 0.3s;
    }
    .gem-btn:hover { background: #3C4043; border-color: #58a6ff; cursor: pointer; }

    /* Mobile Responsiveness */
    @media (max-width: 768px) { .stChatInput { width: 90%; left: 5%; transform: none; } }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "home"
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

# --- HELPER FUNCTIONS ---
def navigate(page):
    st.session_state.page = page
    st.rerun()

def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")

def add_msg(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

# ========================================================
# SIDEBAR (NAVIGATION & GEMS)
# ========================================================
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_chat()
    
    st.markdown("### Gems")
    # Dedicated Button for the Courtroom Gem
    if st.button("⚖️ Courtroom Simulator", help="Enter the Virtual Court"): 
        navigate("courtroom")
    
    # Market Scout is a Tool, accessible from Home, but we can add a shortcut
    if st.button("🛒 Market Scout (Tool)", help="Compare Policies"): 
        navigate("home") # Redirects to home to use the tool in chat

    st.divider()
    with st.expander("👤 Family Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Dad (Heart Patient)...")

# ========================================================
# PAGE 1: HOME (Chat + Upload + Tools)
# ========================================================
if st.session_state.page == "home":
    
    # 1. UPLOAD AREA (Auto-Collapsing)
    uploader_state = 'collapsed' if 'auditor_report' in st.session_state else 'expanded'
    with st.expander("📎 Upload Document (PDF/Image/Video/Audio)", expanded=(uploader_state=='expanded')):
        uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg", "mp4", "mp3", "wav"], label_visibility="collapsed")
        
    # Processor Logic
    if uploaded_file:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("🧠 Analyzing..."):
                client = utils.initialize_gemini()
                
                # Mime & Data Handling
                ft = uploaded_file.type
                if "pdf" in ft: mime = "application/pdf"
                elif "image" in ft: mime = ft
                elif "video" in ft: mime = "video/mp4"
                elif "audio" in ft: mime = "audio/mp3"
                else: mime = "application/pdf"
                
                data = uploaded_file.getvalue()
                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                # Audit
                report = auditor.generate_risk_assessment(client, "Audit this.", data, mime)
                if report:
                    reviewed = critic.review_report(client, report, "Review")
                    st.session_state.auditor_report = reviewed
                    
                    msg = f"✅ **Analysis Complete:** {reviewed.get('summary')}\n\n🚩 **Risks:** {reviewed.get('bad_clauses')}"
                    add_msg("assistant", msg)
                    st.rerun()

    # 2. CHAT DISPLAY
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # 3. INPUT AREA (Voice + Text)
    audio_val = st.audio_input("🎙️") 
    prompt = st.chat_input("Ask 'Compare this', 'Is it a scam?', or 'Explain clause'...")

    user_input = None
    if audio_val:
        # Audio Logic (Simplified for brevity)
        user_input = "Audio message received." # In real app, transcribe here
    elif prompt:
        user_input = prompt

    if user_input:
        add_msg("user", user_input)
        if audio_val: 
            with st.chat_message("user"): st.markdown(user_input)
        else:
            with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("✨ *Thinking...*")
            
            client = utils.initialize_gemini()
            context = st.session_state.get('auditor_report', {})
            
            # ROUTING LOGIC
            prompt_lower = user_input.lower()
            
            if "compare" in prompt_lower or "market" in prompt_lower:
                res = market_scout.compare_policy(client, context) # Market Scout Tool
            
            elif any(x in prompt_lower for x in ["scam", "review", "location", "gwalior"]):
                if "gwalior" in prompt_lower:
                    res = market_scout.check_local_presence(client, context.get('entity_name','Provider'), "Gwalior")
                else:
                    res = market_scout.get_social_sentiment(client, context.get('entity_name','Provider'))
            
            elif "court" in prompt_lower:
                res = "Please switch to 'Courtroom Mode' from the Sidebar to fight a case."
            
            else:
                # Universal Chat
                web_data = search_engine.search_web(user_input)
                final_prompt = f"Context: {context}\nWeb: {web_data}\nUser: {user_input}"
                try:
                    api_res = client.models.generate_content(model='gemini-2.5-pro', contents=final_prompt)
                    res = api_res.text
                except:
                    res = client.models.generate_content(model='gemini-2.5-flash', contents=final_prompt).text
            
            placeholder.markdown(res)
            add_msg("assistant", res)
            if audio_val: st.rerun()

# ========================================================
# PAGE 2: COURTROOM (Dedicated Gem)
# ========================================================
elif st.session_state.page == "courtroom":
    st.markdown("## ⚖️ Virtual Courtroom")
    if st.button("← Exit Simulation"): navigate("home")
    
    st.info("This is a dedicated Simulator. Upload evidence (Video/Audio) in Home first for best results.")
    
    # Courtroom specific input
    claim = st.chat_input("State your claim (e.g. Cataract rejected)...")
    if claim:
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("👨‍⚖️ Examining Case..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Evidence Uploaded")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
