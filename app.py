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

# --- Sidebar Navigation (Gemini Style) ---
with st.sidebar:
    # 1. New Chat Button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_view = "Chat"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Gems (Features)
    st.markdown("### Gems")
    
    if st.button("⚖️ Courtroom Simulator", use_container_width=True):
        st.session_state.current_view = "Courtroom"
        st.rerun()
        
    if st.button("👥 My Family", use_container_width=True):
        st.session_state.current_view = "Family"
        st.rerun()

    if st.button("🛡️ Policy Auditor", use_container_width=True):
         # Just a shortcut to chat with context
         st.session_state.current_view = "Chat"
         st.rerun()

    st.markdown("### Recent")
    st.caption("Today")
    st.caption("Policy Review - HDFC Ergo")
    st.caption("Claim Rejection Help")
    
    st.markdown("---")
    
    # Settings at Bottom
    with st.expander("⚙️ Settings", expanded=False):
        st.checkbox("🔒 Incognito Mode", value=False)
        if st.session_state.get("admin_revealed", False):
            if st.button("🔐 Admin Dashboard"):
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
if st.session_state.current_view == "Chat":
    # Header
    st.markdown('<div class="glow-header">Hello, <span style="color:#4b90ff">User</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-sub">How can I help you today?</div>', unsafe_allow_html=True)
    
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "result_card":
                render_result_card(msg["content"])
            else:
                st.markdown(msg["content"])
    
    # Spacer to push input to bottom
    st.markdown("<br>" * 2, unsafe_allow_html=True)

    # Tools & Input Area (Simulated "Inside" Box)
    with st.container():
        # Tools Menu (Appears above input)
        with st.expander("✨ Tools & Uploads", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            
            # File Uploads
            pdf = c1.file_uploader("📄 PDF", type=["pdf"], key="pdf_up", label_visibility="collapsed")
            audio = c2.file_uploader("🎤 Audio", type=["mp3"], key="audio_up", label_visibility="collapsed")
            
            # Action Buttons
            if c3.button("📊 Full Report"):
                st.session_state.trigger_report = True
                st.toast("Generating Full Report...")
            
            if c4.button("🖼️ Gen Image"):
                 st.toast("Image Gen Feature Coming Soon")

        # Chat Input
        if prompt := st.chat_input("Ask Gemini..."):
            # Handle Special Commands
            if prompt.strip() == "/godmode":
                st.session_state.admin_revealed = True
                st.toast("🔓 God Mode Enabled")
                time.sleep(1)
                st.rerun()

            # User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # AI Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Check for Full Report Trigger
                        if st.session_state.get("trigger_report"):
                            st.session_state.trigger_report = False
                            # Simulate Report Generation
                            response = "Here is the comprehensive report based on the available data..."
                            # (In real app, call a specific agent)
                        else:
                            # Standard Chat
                            response = engine.run_genesis_agent(
                                prompt=prompt, 
                                context=st.session_state.get('policy_text', '')
                            )
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Auto-detect need for report (Simple keyword check)
                        if "analyze" in prompt.lower() or "audit" in prompt.lower():
                             st.info("💡 Tip: Use the 'Full Report' tool for a deep-dive analysis.")
                             
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# 2. COURTROOM VIEW
elif st.session_state.current_view == "Courtroom":
    st.title("⚖️ Courtroom Simulator")
    # ... (Keep existing Courtroom logic, just ensure it renders correctly)
    # Split Screen Layout
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.subheader("📝 Case Preparation")
        st.info("Configure the parameters for the legal battle.")
        
        scenario = st.text_area("Dispute Scenario", "Claim rejected due to 'Pre-existing Disease' clause.")
        user_fact = st.text_input("Your Key Argument", "I disclosed it in the proposal form.")
        
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
                for line in case_data.get("script", []):
                    time.sleep(0.5) # Faster for demo
                    icon = "🗣️"
                    if line["type"] == "judge": icon = "👨‍⚖️"
                    elif line["type"] == "prosecution": icon = "👹"
                    elif line["type"] == "defense": icon = "🛡️"
                    st.markdown(f"**{icon} {line['speaker']}**")
                    st.info(line['text'])
        else:
            st.markdown("<br><br><center>Waiting for Case...</center>", unsafe_allow_html=True)

# 3. FAMILY VIEW (My Family)
elif st.session_state.current_view == "Family":
    st.title("👥 My Family")
    
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
