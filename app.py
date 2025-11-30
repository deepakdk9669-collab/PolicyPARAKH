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

    if st.button("🩺 Medical Expert", use_container_width=True):
        st.session_state.current_view = "Medical"
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
                with st.spinner("Orchestrating Agents..."):
                    try:
                        # 0. Check for Manual Triggers
                        if st.session_state.get("trigger_report"):
                             st.session_state.trigger_report = False
                             prompt = "Generate Full Report" # Override prompt
                             active_agents = ["AUDITOR"]
                        else:
                            # 1. Smart Router (Multi-Agent)
                            active_agents = engine.smart_router(prompt)
                        
                        # Display active agents
                        if len(active_agents) > 1:
                            st.caption(f"⚡ Activated Agents: {', '.join(active_agents)}")
                        
                        # 2. Execute Agents
                        responses = []
                        
                        # A. AUDITOR (Policy Analysis)
                        if "AUDITOR" in active_agents:
                            with st.status("🛡️ Auditor Agent Working...", expanded=False) as status:
                                from agents.auditor import AuditorAgent
                                from agents.critic import CriticAgent
                                
                                auditor = AuditorAgent()
                                critic = CriticAgent()
                                
                                # If asking for full report vs specific question
                                if "report" in prompt.lower() or "audit" in prompt.lower():
                                    status.write("🔍 Auditor: Analyzing Policy...")
                                    res = auditor.generate_full_report(st.session_state.get("policy_text", ""))
                                    
                                    # CRITIC REVIEW
                                    status.write("🧐 Critic: Reviewing findings...")
                                    review = critic.review_audit(st.session_state.get("policy_text", ""), res)
                                    
                                    if review.get("is_accurate"):
                                        res += "\n\n> ✅ **Verified by Critic Agent**"
                                    else:
                                        res += f"\n\n> ⚠️ **Critic Alert:** {review.get('corrections', 'Potential inaccuracies found.')}"
                                        if review.get("missing_clauses"):
                                            res += f"\n> **Missing Clauses:** {', '.join(review['missing_clauses'])}"
                                else:
                                    # Simple check
                                    res = engine.run_genesis_agent(f"As Policy Auditor, answer: {prompt}", context=st.session_state.get("policy_text", ""))
                                
                                status.update(label="🛡️ Audit Complete", state="complete", expanded=False)
                                responses.append(res)

                        # B. MEDICAL (Health Expert)
                        if "MEDICAL" in active_agents:
                            with st.status("🩺 Medical Expert Analyzing...", expanded=False):
                                from agents.medical_expert import MedicalExpertAgent
                                med_expert = MedicalExpertAgent()
                                res = med_expert.analyze_medical_report(prompt, st.session_state.get("policy_text", ""))
                                responses.append(res)
                        
                        # C. TENANT (Rent Agreement)
                        if "TENANT" in active_agents:
                            with st.status("🏠 Tenant Guardian Auditing...", expanded=False):
                                from agents.tenant_guardian import TenantGuardianAgent
                                tenant_agent = TenantGuardianAgent()
                                audit = tenant_agent.audit_rent_agreement(st.session_state.get("policy_text", ""))
                                res = f"### 🏠 Rent Agreement Audit\n**Risk Score:** {audit.get('risk_score')}/100\n\n"
                                res += f"- **Lock-in:** {audit.get('lock_in')}\n"
                                res += f"- **Security Deposit:** {audit.get('security_deposit')}\n"
                                res += f"- **Maintenance:** {audit.get('maintenance')}\n"
                                res += f"\n**Verdict:** {audit.get('risk_reason')}"
                                responses.append(res)

                        # D. CAREER (Job Offer)
                        if "CAREER" in active_agents:
                            with st.status("💼 Career Shield Auditing...", expanded=False):
                                from agents.career_shield import CareerShieldAgent
                                career_agent = CareerShieldAgent()
                                audit = career_agent.audit_offer_letter(st.session_state.get("policy_text", ""))
                                res = f"### 💼 Job Offer Audit\n**Safety Score:** {audit.get('risk_score')}/100\n\n"
                                res += f"- **Bond:** {audit.get('bond')}\n"
                                res += f"- **Notice Period:** {audit.get('notice_period')}\n"
                                res += f"- **Non-Compete:** {audit.get('non_compete')}\n"
                                res += f"\n**Verdict:** {audit.get('risk_reason')}"
                                responses.append(res)

                        # E. SCOUT (Market Comparison)
                        if "SCOUT" in active_agents:
                            with st.status("🔭 Market Scout Searching...", expanded=False):
                                from agents.scout import ScoutAgent
                                scout = ScoutAgent()
                                # Mock user profile for now, or use family memory
                                res = scout.compare_policies("Current Policy", "Family of 3, Age 30")
                                responses.append(res)

                        # F. SENTINEL (Reputation Check)
                        if "SENTINEL" in active_agents:
                            with st.status("🕵️ Sentinel Patroling...", expanded=False):
                                from agents.sentinel import SentinelAgent
                                sentinel = SentinelAgent()
                                # Extract company name from prompt or context
                                company_name = "Insurance Company" # Placeholder, ideally extracted via AI
                                if "star" in prompt.lower(): company_name = "Star Health"
                                elif "hdfc" in prompt.lower(): company_name = "HDFC Ergo"
                                
                                res = sentinel.check_reputation(company_name)
                                responses.append(f"### 🕵️ Sentinel Report for {company_name}\n{res}")

                        # G. LAWYER (Dispute)
                        if "LAWYER" in active_agents:
                             st.toast("⚖️ Legal Dispute Detected", icon="👨‍⚖️")
                             cols = st.columns([3, 1])
                             cols[0].info("This requires a legal strategy session.")
                             if cols[1].button("Open Courtroom"):
                                 st.session_state.current_view = "Courtroom"
                                 st.rerun()
                             responses.append("I've prepared the Courtroom Simulator for your legal dispute. Please proceed there for a full trial simulation.")

                        # H. ARCHITECT (Financials)
                        if "ARCHITECT" in active_agents:
                             with st.status("📉 Architect Forecasting...", expanded=False):
                                 from agents.architect import ArchitectAgent
                                 architect = ArchitectAgent()
                                 # Default cover 5L for demo
                                 fig = architect.forecast_financials(500000)
                                 st.plotly_chart(fig, use_container_width=True)
                                 responses.append("📈 **Financial Forecast:** I've generated a chart showing the impact of medical inflation on your cover over the next 10 years.")

                        # I. GENESIS (General Chat / Fallback)
                        if "GENESIS" in active_agents or not responses:
                            res = engine.run_genesis_agent(
                                prompt=prompt, 
                                context=st.session_state.get('policy_text', '')
                            )
                            responses.append(res)
                        
                        # 3. Combine & Display Responses
                        final_response = "\n\n---\n\n".join(responses)
                        st.markdown(final_response)
                        st.session_state.messages.append({"role": "assistant", "content": final_response})
                             
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

# 4. MEDICAL EXPERT VIEW
elif st.session_state.current_view == "Medical":
    st.title("🩺 Medical Expert")
    st.caption("Dr. Gemini - Your Personal Medical Claims Assistant")
    
    with st.container():
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Analyze Medical Report")
            report_text = st.text_area("Paste Report / Diagnosis Text", height=200, placeholder="e.g. Patient diagnosed with Grade 2 Cataract...")
            
            if st.button("🔍 Analyze Report", type="primary"):
                if report_text:
                    from agents.medical_expert import MedicalExpertAgent
                    expert = MedicalExpertAgent()
                    with st.spinner("Dr. Gemini is analyzing..."):
                        analysis = expert.analyze_medical_report(report_text, st.session_state.get("policy_text", ""))
                        st.markdown(analysis)
                else:
                    st.warning("Please enter some text to analyze.")
                    
        with c2:
            st.subheader("Explain Term")
            term = st.text_input("Enter Medical Term", placeholder="e.g. Angioplasty")
            if st.button("Explain"):
                if term:
                    from agents.medical_expert import MedicalExpertAgent
                    expert = MedicalExpertAgent()
                    with st.spinner("Consulting dictionary..."):
                        explanation = expert.explain_term(term)
                        st.info(explanation)
