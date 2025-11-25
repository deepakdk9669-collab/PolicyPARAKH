import streamlit as st
import utils
import auditor
import sentinel
import architect
import courtroom
import market_scout
import uuid

# --- PAGE CONFIG & STYLING ---
st.set_page_config(page_title="PolicyPARAKH AI", layout="wide", initial_sidebar_state="expanded")

# Dark Mode & Mobile UI CSS mimicking the screenshot
st.markdown("""
<style>
    /* Global Font & Dark Theme adjustments */
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .sidebar-btn { width: 100%; text-align: left; padding: 10px; border-radius: 8px; background: transparent; color: #C9D1D9; border: none; margin-bottom: 5px; }
    .sidebar-btn:hover { background-color: #21262D; cursor: pointer; }
    .sidebar-header { color: #8B949E; font-size: 0.8rem; font-weight: 600; margin-top: 20px; margin-bottom: 10px; text-transform: uppercase; }
    
    /* Main Chat Area */
    .chat-container { max-width: 900px; margin: 0 auto; padding-bottom: 100px; }
    
    /* Custom Badge */
    .gem-badge { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    
    /* Input Area styling fix */
    .stChatInput { position: fixed; bottom: 0; left: 0; right: 0; padding: 20px; background: #0E1117; z-index: 100; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT ---
if "sessions" not in st.session_state:
    # Structure: {session_id: {'title': str, 'messages': []}}
    st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'title': "New Chat", 'messages': []}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state:
    st.session_state.family_profile = ""

# --- FUNCTIONS ---
def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'title': "New Chat", 'messages': []}
    st.session_state.current_session_id = new_id
    # Reset file data for new chat context
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    if 'architect_data' in st.session_state: del st.session_state.architect_data

def get_current_messages():
    return st.session_state.sessions[st.session_state.current_session_id]['messages']

def add_message(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})
    # Update title if it's the first user message
    msgs = st.session_state.sessions[st.session_state.current_session_id]['messages']
    if len(msgs) == 2 and msgs[1]['role'] == 'user':
        title = msgs[1]['content'][:25] + "..."
        st.session_state.sessions[st.session_state.current_session_id]['title'] = title

# --- SIDEBAR (Mimicking the Screenshot) ---
with st.sidebar:
    # 1. New Chat Button
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        create_new_chat()
    
    # 2. Family Card (Profile)
    st.markdown("<div class='sidebar-header'>My Profile (Family Card)</div>", unsafe_allow_html=True)
    with st.expander("👨‍👩‍👧‍👦 Edit Family Details"):
        family_input = st.text_area("Ex: Mom (65, Diabetes), Me (30, Smoker)", value=st.session_state.family_profile)
        if st.button("Save Profile"):
            st.session_state.family_profile = family_input
            st.success("Saved!")

    # 3. Gems / Tools (The Blue Print Features)
    st.markdown("<div class='sidebar-header'>Gems (Tools)</div>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("⚖️ Courtroom", help="Simulate a legal battle"):
            add_message("system", "ACTIVATED: Virtual Courtroom Mode. Describe your claim.")
            st.rerun()
    with col_t2:
        if st.button("🛒 Scout", help="Compare with market"):
            add_message("system", "ACTIVATED: Market Scout. Comparing policy...")
            # Trigger scout immediately if report exists
            client = utils.initialize_gemini()
            if 'auditor_report' in st.session_state and client:
                res = market_scout.compare_policy(client, st.session_state.auditor_report)
                add_message("assistant", res)
                st.rerun()
            else:
                add_message("assistant", "Please upload a policy first to compare.")
                st.rerun()

    # 4. Chat History List
    st.markdown("<div class='sidebar-header'>Recent Chats</div>", unsafe_allow_html=True)
    # Reverse to show newest first
    for sess_id, sess_data in list(st.session_state.sessions.items())[::-1]:
        if st.button(f"💬 {sess_data['title']}", key=sess_id, use_container_width=True):
            st.session_state.current_session_id = sess_id
            st.rerun()

# --- MAIN CHAT INTERFACE ---
client = utils.initialize_gemini()

# Header
st.markdown(f"### PolicyPARAKH <span class='gem-badge'>3 Pro</span>", unsafe_allow_html=True)

# File Uploader (Integrated subtly)
uploaded_file = st.file_uploader("📎 Add Policy (PDF/Image)", type=["pdf", "png", "jpg"], label_visibility="collapsed")
if uploaded_file:
    # Processing Logic (Simplified for UI)
    if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        with st.spinner("Processing..."):
            if uploaded_file.type == "application/pdf":
                data = utils.base64_encode_pdf(uploaded_file)
            else:
                import base64
                data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            
            st.session_state.file_data = data
            st.session_state.current_file_name = uploaded_file.name
            
            # Auto-Run Auditor on upload
            report = auditor.generate_risk_assessment(client, "Scan this.", data)
            st.session_state.auditor_report = report
            add_message("assistant", f"📄 **Policy Uploaded & Scanned!**\n\n**Risk Score:** {report.get('risk_score_0_to_100')}/100\n\n{report.get('auditor_summary')}")
            
            # Check Family Card conflicts
            if st.session_state.family_profile:
                fam_check = client.models.generate_content(
                    model='gemini-3-pro-preview',
                    contents=f"Policy Risks: {report}. Family Profile: {st.session_state.family_profile}. Cross-reference and warn me."
                )
                add_message("assistant", f"⚠️ **Family Alert:** {fam_check.text}")

# Chat Area
chat_container = st.container()
with chat_container:
    for msg in get_current_messages():
        if msg['role'] == 'system':
            st.info(msg['content'])
        else:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# Bottom Input Bar
if prompt := st.chat_input("Ask about your policy, start a courtroom battle..."):
    add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ""
        
        # 1. Check if Courtroom Mode is implied
        if "court" in prompt.lower() or "lawyer" in prompt.lower():
            if 'auditor_report' in st.session_state:
                response = courtroom.run_courtroom_simulation(client, st.session_state.auditor_report, prompt)
            else:
                response = "Please upload a policy first to start the courtroom simulation."
        
        # 2. Check if Sentinel (Scam/News) is needed
        elif any(x in prompt.lower() for x in ["scam", "news", "fraud"]):
            response = sentinel.sentinel_agent_check(client, st.session_state.get('auditor_report', {}), prompt)
            
        # 3. Check if Architect (Value) is needed
        elif "value" in prompt.lower() or "inflation" in prompt.lower():
             df = architect.architect_agent_forecast(client, {}) # Pass empty dict if no report, handles itself
             st.session_state.architect_data = df
             response = "I've generated the Inflation Forecast chart. Expand the tool section to view it."
             st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])

        # 4. Default Chat (Gemini 3 Pro)
        else:
            context = f"""
            System: You are PolicyPARAKH.
            Family Context: {st.session_state.family_profile}
            Current Policy Report: {st.session_state.get('auditor_report', 'None uploaded')}
            User: {prompt}
            """
            res = client.models.generate_content(model='gemini-3-pro-preview', contents=context)
            response = res.text

        st.markdown(response)
        add_message("assistant", response)
