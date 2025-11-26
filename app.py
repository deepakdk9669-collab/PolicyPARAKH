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
    
    /* Floating Input Container (The "One Box") */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #131314; /* Match background to hide overlap */
        padding: 20px 10% 10px 10%; /* Centered with padding */
        z-index: 1000;
        border-top: 1px solid #333;
    }
    
    /* Tool Chips (Multiselect Styling) */
    .stMultiSelect span {
        background-color: #28292A;
        border: 1px solid #444;
        color: #E3E3E3;
        border-radius: 20px;
    }
    
    /* Chat Input Styling */
    .stChatInput {
        padding-bottom: 50px; /* Make space for the floating container */
    }
    
    /* Chat Bubbles */
    .stChatMessage { background-color: transparent; }
    
    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .input-container { padding: 10px 5%; }
    }
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
def navigate(page): st.session_state.page = page; st.rerun()
def add_msg(role, content): st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")

# ========================================================
# SIDEBAR (Gemini Layout)
# ========================================================
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"): new_chat()
    
    st.markdown("### Recent")
    sorted_sessions = list(st.session_state.sessions.items())[::-1]
    for sess_id, data in sorted_sessions[:5]: # Show last 5
        if st.button(f"💬 {data.get('title', 'Chat')[:20]}...", key=sess_id):
            st.session_state.current_session_id = sess_id
            navigate("home")

    st.divider()
    st.markdown("### Gems")
    if st.button("⚖️ Courtroom Simulator", use_container_width=True): navigate("courtroom")
    
    with st.expander("👤 Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Mom (Diabetes)")

# ========================================================
# PAGE 1: HOME (Unified Experience)
# ========================================================
if st.session_state.page == "home":
    
    # Greeting
    if not st.session_state.sessions[st.session_state.current_session_id]['messages']:
        st.markdown("# Hello, Chief.")
        st.markdown("### I'm ready. Select tools or upload evidence.")

    # CHAT HISTORY
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # --- THE "ONE BOX" INPUT AREA ---
    # We use a container at the bottom to group everything
    
    with st.container():
        # 1. Tool Selection (The "Chips")
        selected_tools = st.multiselect(
            "Active Tools", 
            ["Auditor", "Architect", "Sentinel", "Market Scout"], 
            default=["Auditor"],
            label_visibility="collapsed",
            placeholder="Select Tools (e.g. Scout, Architect)..."
        )
        
        # 2. File Uploader (Compact)
        with st.expander("kB Upload Evidence (PDF/Img/Video)", expanded=False):
            uploaded_file = st.file_uploader("File", type=["pdf", "png", "jpg", "mp4", "mp3"], label_visibility="collapsed")

        # 3. Audio Input (Mic)
        audio_val = st.audio_input("🎙️") 

        # 4. Main Text Input
        prompt = st.chat_input("Ask anything...")

    # --- PROCESSING LOGIC ---
    
    client = utils.initialize_gemini()
    
    # A. Handle File (Auditor)
    if uploaded_file and client:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("🧠 Analyzing..."):
                ft = uploaded_file.type
                mime = "application/pdf" if "pdf" in ft else (ft if "image" in ft else ("video/mp4" if "video" in ft else ("audio/mp3" if "audio" in ft else "application/pdf")))
                
                if "pdf" in mime: data = utils.base64_encode_pdf(uploaded_file)
                else: import base64; data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                report = auditor.generate_risk_assessment(client, "Analyze.", data, mime)
                if report:
                    st.session_state.auditor_report = report
                    msg = f"✅ **Analyzed:** {report.get('summary')}"
                    add_msg("assistant", msg)
                    st.rerun()

    # B. Handle Input (Text/Audio)
    user_input = None
    if audio_val: user_input = "Audio received (Processing...)" 
    elif prompt: user_input = prompt

    if user_input:
        add_msg("user", user_input)
        if audio_val: 
            with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            
            context = st.session_state.get('auditor_report', {})
            prompt_lower = user_input.lower()
            final_response = ""

            # --- TOOL ORCHESTRATION ---
            
            # Scout
            if "Market Scout" in selected_tools or any(x in prompt_lower for x in ["compare", "market"]):
                res = market_scout.compare_policy(client, context)
                final_response += f"\n\n🛒 **Scout:** {res}"
            
            # Sentinel
            if "Sentinel" in selected_tools or any(x in prompt_lower for x in ["scam", "review"]):
                entity = context.get('entity_name', 'Company')
                res = market_scout.get_social_sentiment(client, entity)
                final_response += f"\n\n📢 **Sentinel:** {res}"
            
            # Architect
            if "Architect" in selected_tools or "value" in prompt_lower:
                df = architect.architect_agent_forecast(client, {})
                st.session_state.architect_data = df
                final_response += "\n\n📉 **Architect:** Inflation chart ready."

            # Fallback Chat
            if not final_response:
                web = search_engine.search_web(user_input)
                try:
                    api_res = client.models.generate_content(model='gemini-2.5-pro', contents=f"Context:{context}\nWeb:{web}\nUser:{user_input}")
                    final_response = api_res.text
                except: final_response = "Error."

            placeholder.markdown(final_response)
            add_msg("assistant", final_response)
            
            if 'architect_data' in st.session_state and "Architect" in final_response:
                st.line_chart(st.session_state.architect_data.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])
                
            if audio_val: st.rerun()

# ========================================================
# PAGE 2: COURTROOM (Gem)
# ========================================================
elif st.session_state.page == "courtroom":
    st.markdown("## ⚖️ Courtroom Simulator")
    if st.button("← Back"): navigate("home")
    
    if claim := st.chat_input("State claim..."):
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("Fighting..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Evidence")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
