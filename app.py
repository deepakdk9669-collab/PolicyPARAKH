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
st.set_page_config(page_title="PolicyPARAKH Gemini", layout="wide", initial_sidebar_state="expanded")

# --- GEMINI CLONE CSS ---
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp { background-color: #131314; color: #E3E3E3; font-family: 'Google Sans', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #1E1F20; border-right: 1px solid #333; }
    
    /* Floating Input Container */
    .input-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 70%;
        background-color: #1E1F20;
        border-radius: 25px;
        border: 1px solid #444;
        padding: 10px;
        z-index: 1000;
        display: flex;
        align-items: center;
    }
    
    /* Remove default Streamlit padding for cleaner look */
    .block-container { padding-top: 2rem; padding-bottom: 10rem; }
    
    /* Gem/Tool Button Styling */
    .gem-btn {
        width: 100%;
        padding: 10px;
        margin: 2px 0;
        background: transparent;
        color: #E3E3E3;
        border: none;
        text-align: left;
        border-radius: 20px;
    }
    .gem-btn:hover { background: #333; }
    
    /* Chat Bubbles */
    .stChatMessage { background-color: transparent; }
    
    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
if "active_tools" not in st.session_state: st.session_state.active_tools = []

# --- HELPER FUNCTIONS ---
def navigate(page): st.session_state.page = page; st.rerun()
def add_msg(role, content): st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")

# ========================================================
# SIDEBAR (The Gemini Layout)
# ========================================================
with st.sidebar:
    # 1. New Chat
    if st.button("➕ New Chat", use_container_width=True, type="primary"): new_chat()
    
    # 2. Search History
    search_q = st.text_input("🔍 Search chats", placeholder="Search...", label_visibility="collapsed")
    
    st.markdown("### Recent")
    # Filter chats based on search
    sorted_sessions = list(st.session_state.sessions.items())[::-1]
    for sess_id, data in sorted_sessions:
        title = data.get('title', 'Chat')
        if search_q.lower() in title.lower():
            if st.button(f"💬 {title[:20]}...", key=sess_id, use_container_width=True):
                st.session_state.current_session_id = sess_id
                navigate("home")

    st.divider()
    
    # 3. Gems (Courtroom)
    st.markdown("### Gems")
    if st.button("⚖️ Courtroom Simulator", use_container_width=True): navigate("courtroom")
    
    # 4. Profile (Replaces My Stuff)
    with st.expander("👤 User Profile"):
        st.session_state.family_profile = st.text_area("Family Health & Location", value=st.session_state.family_profile, placeholder="Ex: Mom (Diabetes), Gwalior")

# ========================================================
# PAGE 1: HOME (Unified Chat & Tools)
# ========================================================
if st.session_state.page == "home":
    
    # Greeting / Empty State
    if not st.session_state.sessions[st.session_state.current_session_id]['messages']:
        st.markdown("<h1><span style='background: linear-gradient(to right, #4285F4, #9B72CB); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Hello, Chief.</span></h1>", unsafe_allow_html=True)
        st.markdown("### I'm ready. Select tools or upload evidence.")

    # CHAT HISTORY DISPLAY
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # --- THE UNIFIED INPUT BAR (Tools + Upload + Audio + Text) ---
    
    # 1. Tool Selection (Just above chat)
    with st.container():
        # This acts as the "Select Agent" feature
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            # Multi-select for agents/tools
            selected_agents = st.multiselect(
                "🛠️ Active Agents", 
                ["Auditor", "Market Scout", "Sentinel", "Architect"],
                default=["Auditor"],
                label_visibility="collapsed",
                placeholder="Select Agents..."
            )
        
    # 2. Input Area
    # Note: Streamlit chat_input is fixed. We place uploaders near it.
    
    # File Uploader (Expander style to keep it clean like Gemini's '+' button)
    with st.popover("kB", use_container_width=False, help="Upload Media"):
        uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "jpg", "mp4", "mp3"], label_visibility="collapsed")
    
    # Audio Input (The Mic)
    audio_val = st.audio_input("🎙️") 
    
    # Text Input
    prompt = st.chat_input("Ask anything...")

    # --- PROCESSING LOGIC ---
    
    # 1. Handle File Upload (Auditor Agent)
    client = utils.initialize_gemini()
    if uploaded_file and client:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("🧠 Processing Evidence..."):
                # Mime Handling
                ft = uploaded_file.type
                mime = "application/pdf" if "pdf" in ft else (ft if "image" in ft else ("video/mp4" if "video" in ft else ("audio/mp3" if "audio" in ft else "application/pdf")))
                
                if "pdf" in mime: data = utils.base64_encode_pdf(uploaded_file)
                else: import base64; data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                # Audit
                report = auditor.generate_risk_assessment(client, "Analyze this.", data, mime)
                if report:
                    reviewed = critic.review_report(client, report, "Review")
                    st.session_state.auditor_report = reviewed
                    
                    msg = f"✅ **Evidence Analyzed**\n\n**Verdict:** {reviewed.get('summary')}"
                    add_msg("assistant", msg)
                    st.rerun()

    # 2. Handle User Input (Text or Voice)
    user_input = None
    if audio_val: user_input = "Audio Input Received (Processing...)" # Add STT here ideally
    elif prompt: user_input = prompt

    if user_input:
        add_msg("user", user_input)
        if audio_val: with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            
            context = st.session_state.get('auditor_report', {})
            prompt_lower = user_input.lower()
            
            # --- INTER-AGENT ORCHESTRATION ---
            # The Coordinator (Main Brain) decides which selected agents to use
            
            final_response = ""
            
            # 1. Market Scout (If selected or asked)
            if "Market Scout" in selected_agents or any(x in prompt_lower for x in ["compare", "market", "better"]):
                scout_res = market_scout.compare_policy(client, context)
                final_response += f"\n\n🛒 **Market Scout:**\n{scout_res}"
            
            # 2. Sentinel (If selected or asked about scam/reviews)
            if "Sentinel" in selected_agents or any(x in prompt_lower for x in ["scam", "review", "sentiment"]):
                entity = context.get('entity_name', 'Company')
                sentinel_res = market_scout.get_social_sentiment(client, entity)
                final_response += f"\n\n📢 **Sentinel:**\n{sentinel_res}"
                
            # 3. Architect (If selected or asked about money)
            if "Architect" in selected_agents or "value" in prompt_lower:
                df = architect.architect_agent_forecast(client, {})
                st.session_state.architect_data = df
                final_response += "\n\n📉 **Architect:** Inflation forecast generated below."
                
            # 4. General Chat (Fallback or Synthesis)
            if not final_response:
                web = search_engine.search_web(user_input)
                # Inject Family Profile Context
                family_ctx = f"Family Profile: {st.session_state.family_profile}" if st.session_state.family_profile else ""
                
                full_prompt = f"{family_ctx}\nContext:{context}\nWeb:{web}\nUser:{user_input}"
                try:
                    api_res = client.models.generate_content(model='gemini-2.5-pro', contents=full_prompt)
                    final_response = api_res.text
                except: final_response = "Error connecting."

            placeholder.markdown(final_response)
            add_msg("assistant", final_response)
            
            # Show Charts if Architect ran
            if 'architect_data' in st.session_state and "Architect" in final_response:
                st.line_chart(st.session_state.architect_data.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])
            
            if audio_val: st.rerun()

# ========================================================
# PAGE 2: COURTROOM SIMULATOR (Dedicated Gem)
# ========================================================
elif st.session_state.page == "courtroom":
    st.markdown("## ⚖️ Courtroom Simulator")
    if st.button("← Back to Home"): navigate("home")
    
    st.info("Dedicated Simulator Mode. Upload evidence in Home first.")
    
    if claim := st.chat_input("State your claim..."):
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("Fighting..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Evidence")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
