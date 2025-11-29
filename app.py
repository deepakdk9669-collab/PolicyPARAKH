# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import os
import time
from utils.security import SecurityManager
from utils.pdf_loader import extract_text_from_pdf
from utils.memory import FamilyMemory
from utils.market_utils import log_market_intel
from utils.admin_dashboard import render_admin_dashboard
from utils.ui_components import render_member_card, render_result_card

# Page Config
st.set_page_config(
    page_title="PolicyPARAKH",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open("assets/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    st.warning("CSS file not found. Please ensure assets/style.css exists.")

# Initialize Managers
security = SecurityManager()
memory = FamilyMemory()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Chat" # Default View

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/950/950299.png", width=50)
    st.markdown("### PolicyPARAKH")
    
    st.markdown("---")
    
    # Navigation Menu
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
    
    # Settings / BYOK
    with st.expander("⚙️ Settings"):
        groq_key = st.text_input("Groq API Key", type="password")
        if groq_key:
            st.session_state["GROQ_API_KEY"] = groq_key
            st.success("Key Saved")

    # Hidden Admin
    if st.session_state.get("admin_revealed", False):
        st.markdown("---")
        st.caption("🔐 Admin Mode")
        if st.button("Launch Dashboard", key="adm_launch"):
            st.session_state.show_admin = True
            st.rerun()

    st.markdown("---")
    st.caption("© 2025 PolicyPARAKH")

# --- Admin Override ---
if st.session_state.get("show_admin", False):
    render_admin_dashboard()
    st.stop()

# --- Main Views ---

# 1. CHAT VIEW (Default)
if st.session_state.current_view == "Chat":
    st.title("PolicyPARAKH AI")
    st.caption("The Neural Legal Defense System")
    
    # File Upload Area (Top)
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        # Process File
        with open("temp_policy.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        if not st.session_state.processing_complete:
            with st.status("🔍 Analyzing Document...", expanded=True):
                policy_text = extract_text_from_pdf("temp_policy.pdf")
                st.session_state.policy_text = policy_text
                
                # Router & Agents (Simplified for Speed)
                st.write("Router: Classifying...")
                # ... (Agent Logic - Keeping it brief for UI focus) ...
                # Assuming Auditor for demo
                from agents.auditor import AuditorAgent
                auditor = AuditorAgent()
                report = auditor.audit_policy(policy_text)
                st.session_state.audit_report = report
                
                # Log Data
                log_market_intel({"company_name": "Unknown", "risk_score": report.get("risk_score", 0)})
                
                st.session_state.processing_complete = True
                st.session_state.messages.append({"role": "assistant", "type": "result_card", "content": report})
                st.rerun()

    # Chat Stream
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "result_card":
                render_result_card(msg["content"])
            else:
                st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about the policy..."):
        # God Mode
        if prompt.strip() == "/godmode":
            st.session_state.admin_revealed = True
            st.toast("🔓 God Mode Enabled")
            time.sleep(1)
            st.rerun()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=security.get_next_api_key())
                context = st.session_state.get('policy_text', '')[:5000]
                response = llm.invoke(f"Context: {context}\n\nUser: {prompt}").content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# 2. COURTROOM VIEW
elif st.session_state.current_view == "Courtroom":
    st.title("⚖️ Virtual Courtroom Simulator")
    st.markdown("Simulate a legal battle against the insurance company.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Setup Case")
        scenario = st.text_area("Dispute Scenario", "Claim rejected due to 'Pre-existing Disease' clause.")
        user_fact = st.text_input("Your Key Argument", "I disclosed it in the proposal form.")
        
        if st.button("Start Simulation", type="primary"):
            st.session_state.sim_started = True
            
    with col2:
        if st.session_state.get("sim_started"):
            st.subheader("🎬 Live Proceedings")
            
            # Simulation Logic
            from agents.lawyer import CourtroomAgent
            court = CourtroomAgent()
            
            with st.spinner("The Judge is entering..."):
                # Mock Data for Demo
                case_data = court.simulate_argument(
                    st.session_state.get("policy_text", ""), 
                    f"{scenario} User Argument: {user_fact}",
                    "Inflation High",
                    "Reputation Poor"
                )
                
                # Script Playback
                script_container = st.container(height=400)
                for line in case_data.get("script", []):
                    time.sleep(0.8)
                    with script_container:
                        icon = "🗣️"
                        if line["type"] == "judge": icon = "👨‍⚖️"
                        elif line["type"] == "prosecution": icon = "👹"
                        elif line["type"] == "defense": icon = "🛡️"
                        
                        st.markdown(f"**{icon} {line['speaker']}**: {line['text']}")
                
                # Verdict
                verdict = case_data.get("verdict", {})
                st.success(f"**Verdict**: {verdict.get('winner')} ({verdict.get('probability')})")

# 3. FAMILY VIEW
elif st.session_state.current_view == "Family":
    st.title("👥 Family Context")
    st.markdown("Manage your family profile for personalized risk analysis.")
    
    # Add Member Form
    with st.expander("Add New Member"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Name")
        role = c2.selectbox("Role", ["Self", "Spouse", "Child", "Parent"])
        age = c3.number_input("Age", 1, 100, 30)
        if st.button("Add Member"):
            if "family_profile" not in st.session_state: st.session_state.family_profile = []
            st.session_state.family_profile.append({
                "name": name, "role": role, "age": age, 
                "risk_level": "High" if age > 50 else "Low" # Mock logic
            })
            st.success("Member Added")
            st.rerun()
            
    st.divider()
    
    # Display Cards
    if st.session_state.get("family_profile"):
        cols = st.columns(3)
        for idx, member in enumerate(st.session_state.family_profile):
            with cols[idx % 3]:
                render_member_card(member)
    else:
        st.info("No family members added yet.")
