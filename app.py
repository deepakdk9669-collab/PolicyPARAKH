# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import os
import time
from utils.security import SecurityManager
from utils.pdf_loader import extract_text_from_pdf
from utils.memory import FamilyMemory
from utils.market_utils import log_market_intel
from utils.ui_components import render_member_card, render_result_card
from utils.ai_engine import AIEngine

# Page Config
st.set_page_config(
    page_title="PolicyPARAKH 2.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    try:
        with open("assets/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Initialize Managers
security = SecurityManager()
memory = FamilyMemory()
engine = AIEngine()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Chat"
if "family_profile" not in st.session_state:
    st.session_state.family_profile = []

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/950/950299.png", width=60)
    st.markdown("## PolicyPARAKH")
    st.caption("Neural Legal Defense System")
    
    st.markdown("---")
    
    # Navigation
    if st.button("💬 AI Chat", use_container_width=True):
        st.session_state.current_view = "Chat"
        st.rerun()
        
    if st.button("⚖️ Courtroom Sim", use_container_width=True):
        st.session_state.current_view = "Courtroom"
        st.rerun()
        
    if st.button("👥 Family Context", use_container_width=True):
        st.session_state.current_view = "Family"
        st.rerun()

    st.markdown("---")
    
    # Family Card Preview (Mini)
    if st.session_state.family_profile:
        st.markdown("#### 👨‍👩‍👧‍👦 Active Family")
        for member in st.session_state.family_profile[:2]: # Show max 2
            st.caption(f"• {member['name']} ({member['role']})")
    
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Settings", expanded=False):
        st.checkbox("🔒 Incognito Mode", value=False, help="Do not save data to Market Intel.")
        groq_key = st.text_input("Groq API Key (Optional)", type="password")
        if groq_key:
            st.session_state["GROQ_API_KEY"] = groq_key
            
    # Admin Access
    if st.session_state.get("admin_revealed", False):
        st.markdown("---")
        if st.button("🔐 Admin Dashboard", use_container_width=True):
            st.session_state.show_admin = True
            st.rerun()

# --- Admin Redirect ---
if st.session_state.get("show_admin", False):
    from pages.admin_panel import render_admin_dashboard
    render_admin_dashboard()
    if st.sidebar.button("🔙 Back to App"):
        st.session_state.show_admin = False
        st.rerun()
    st.stop()

# --- Main Views ---

# 1. CHAT VIEW
# 1. CHAT VIEW
if st.session_state.current_view == "Chat":
    st.markdown('<div class="glow-header">PolicyPARAKH <span style="color:#4b90ff">AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-sub">Neural Legal Defense System • Genesis Brain Online</div>', unsafe_allow_html=True)
    
    # Multimedia Input Zone
    with st.expander("📂 Upload Evidence (PDF, Audio, Video)", expanded=True):
        c1, c2, c3 = st.columns(3)
        uploaded_file = c1.file_uploader("Contract (PDF)", type=["pdf"], key="pdf_up")
        audio_evidence = c2.file_uploader("Verbal Defense (Audio)", type=["mp3", "wav"], key="audio_up")
        video_evidence = c3.file_uploader("Damage Evidence (Video)", type=["mp4", "mov"], key="video_up")

    if uploaded_file:
        # Process PDF
        with open("temp_policy.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        if not st.session_state.processing_complete:
            with st.status("🔍 Analyzing Document...", expanded=True):
                policy_text = extract_text_from_pdf("temp_policy.pdf")
                st.session_state.policy_text = policy_text
                
                # Router Logic (Simplified)
                st.write("🤖 Router: Classifying Document...")
                # Default to Auditor for now
                from agents.auditor import AuditorAgent
                auditor = AuditorAgent()
                report = auditor.audit_policy(policy_text)
                
                # Log Data
                log_market_intel({"company_name": "Unknown", "risk_score": report.get("risk_score", 0)})
                
                st.session_state.processing_complete = True
                st.session_state.messages.append({"role": "assistant", "type": "result_card", "content": report})
                st.rerun()

    # Chat Interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "result_card":
                render_result_card(msg["content"])
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about the policy..."):
        if prompt.strip() == "/godmode":
            st.session_state.admin_revealed = True
            st.toast("🔓 God Mode Enabled")
            time.sleep(1)
            st.rerun()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use Genesis Brain (Gemini 3.0 Pro)
                    response = engine.run_genesis_agent(
                        prompt=prompt, 
                        context=st.session_state.get('policy_text', '')
                    )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# 2. COURTROOM VIEW (Split Screen)
elif st.session_state.current_view == "Courtroom":
    st.title("⚖️ Virtual Courtroom Simulator")
    
    # Split Screen Layout
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.subheader("📝 Case Preparation")
        st.info("Configure the parameters for the legal battle.")
        
        scenario = st.text_area("Dispute Scenario", "Claim rejected due to 'Pre-existing Disease' clause.")
        user_fact = st.text_input("Your Key Argument", "I disclosed it in the proposal form.")
        
        st.markdown("### Evidence Locker")
        st.checkbox("Include Uploaded PDF", value=True)
        st.checkbox("Include Audio Testimony", value=False)
        
        if st.button("🔥 Commence Trial", type="primary", use_container_width=True):
            st.session_state.sim_started = True

    with right_col:
        st.subheader("🎬 Live Proceedings")
        
        if st.session_state.get("sim_started"):
            from agents.lawyer import CourtroomAgent
            court = CourtroomAgent()
            
            with st.spinner("The Judge is entering..."):
                case_data = court.simulate_argument(
                    st.session_state.get("policy_text", ""), 
                    f"{scenario} User Argument: {user_fact}"
                )
                
                # Script Playback
                script_container = st.container(height=500)
                for line in case_data.get("script", []):
                    time.sleep(1.0)
                    with script_container:
                        icon = "🗣️"
                        if line["type"] == "judge": icon = "👨‍⚖️"
                        elif line["type"] == "prosecution": icon = "👹"
                        elif line["type"] == "defense": icon = "🛡️"
                        elif line["type"] == "witness": icon = "🕵️"
                        
                        st.markdown(f"**{icon} {line['speaker']}**")
                        st.info(line['text'])
                
                # Verdict
                verdict = case_data.get("verdict", {})
                if verdict.get("winner") == "Consumer":
                    st.success(f"**Verdict**: {verdict.get('winner')} ({verdict.get('probability')})")
                    st.balloons()
                else:
                    st.error(f"**Verdict**: {verdict.get('winner')} ({verdict.get('probability')})")

        else:
            st.markdown(
                """
                <div style='text-align: center; padding: 50px; color: #666;'>
                    <h3>Waiting for Case...</h3>
                    <p>Setup the scenario on the left to begin.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

# 3. FAMILY VIEW
elif st.session_state.current_view == "Family":
    st.title("👥 Family Context")
    
    with st.expander("Add New Member", expanded=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Name")
        role = c2.selectbox("Role", ["Self", "Spouse", "Child", "Parent"])
        age = c3.number_input("Age", 1, 100, 30)
        
        if st.button("Save Member"):
            st.session_state.family_profile.append({
                "name": name, "role": role, "age": age, 
                "risk_level": "High" if age > 50 else "Low"
            })
            st.success("Member Added")
            st.rerun()
            
    st.divider()
    
    if st.session_state.family_profile:
        cols = st.columns(3)
        for idx, member in enumerate(st.session_state.family_profile):
            with cols[idx % 3]:
                render_member_card(member)
    else:
        st.info("No family members added yet.")
