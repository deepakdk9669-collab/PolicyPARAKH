# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import os
import time
from utils.security import SecurityManager
from utils.pdf_loader import extract_text_from_pdf
from utils.memory import FamilyMemory
from utils.market_utils import log_market_intel
from utils.admin_dashboard import render_admin_dashboard

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

# --- Sidebar: The Command Center ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/950/950299.png", width=60)
    st.markdown("## PolicyPARAKH")
    st.caption("Universal Contract Guardian")
    
    st.divider()
    
    # 1. Courtroom Simulator (Moved from Main)
    with st.expander("⚖️ Courtroom Simulator"):
        st.caption("Simulate a legal battle.")
        scenario = st.text_area("Dispute Scenario", "Claim rejected for 2-year waiting period.")
        if st.button("Start Simulation"):
            st.session_state.show_courtroom = True
    
    # 2. Family Context (Moved from Main)
    with st.expander("👥 Family Context"):
        st.caption("Personalized Risk Analysis")
        if st.session_state.get('family_profile'):
            for m in st.session_state['family_profile']:
                st.code(f"{m['name']} ({m['role']})")
        else:
            st.info("No profile set.")
            
        if st.button("Edit Profile"):
            st.session_state.show_profile_editor = True

    st.divider()
    
    # 3. BYOK
    with st.expander("🔐 BYOK Protocol"):
        groq_key = st.text_input("Groq API Key", type="password")
        if groq_key:
            st.session_state["GROQ_API_KEY"] = groq_key
            st.success("Hybrid Brain Active")

    st.divider()

    # 4. Deep Memory (Past Verdicts)
    with st.expander("📂 Case History (Deep Memory)"):
        history = memory.get_case_history()
        if history:
            for case in history:
                st.caption(f"📅 {time.strftime('%Y-%m-%d %H:%M', time.localtime(case['timestamp']))}")
                st.write(f"**Scenario:** {case['scenario'][:50]}...")
                st.success(f"**Verdict:** {case['verdict'].get('winner')}")
                st.markdown("---")
        else:
            st.info("No cases argued yet.")

    st.divider()
    
    # --- Hidden Admin Access ---
    # --- Hidden Admin Access (God Mode) ---
    if st.session_state.get("admin_revealed", False):
        with st.expander("🔐 Admin Access", expanded=True):
            if "admin_authenticated" not in st.session_state:
                st.session_state.admin_authenticated = False
                
            if st.session_state.admin_authenticated:
                if st.button("Launch Dashboard"):
                    st.session_state.show_admin = True
                    st.rerun()
                if st.button("Logout", key="sidebar_logout"):
                    st.session_state.admin_authenticated = False
                    st.session_state.show_admin = False
                    st.session_state.admin_revealed = False # Hide again
                    st.rerun()
            else:
                admin_pass = st.text_input("Password", type="password", key="sidebar_admin_pass")
                if st.button("Login", key="sidebar_login"):
                    admin_key = st.secrets.get("ADMIN_KEY", "admin123")
                    if admin_pass == admin_key:
                        st.session_state.admin_authenticated = True
                        st.success("Access Granted")
                        st.rerun()
                    else:
                        st.error("Invalid")

    st.divider()
    st.markdown("---")
    st.caption("© 2025 PolicyPARAKH | Created by Deepak Kushwah")

# --- Main Interface ---

# Check for Admin Mode
if st.session_state.get("show_admin", False):
    render_admin_dashboard()
    st.stop() # Stop rendering the rest of the app

# Header
st.markdown("<h1 style='text-align: center;'>PolicyPARAKH AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>The Neural Legal Defense System</p>", unsafe_allow_html=True)

# File Upload (The Trigger)
uploaded_file = st.file_uploader("Upload Contract (PDF)", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    # Save & Extract
    with open("temp_policy.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if not st.session_state.processing_complete:
        with st.status("🔍 Analyzing Document...", expanded=True) as status:
            st.write("Extracting Text...")
            policy_text = extract_text_from_pdf("temp_policy.pdf")
            st.session_state.policy_text = policy_text
            
            # 1. Router Agent (The Gateway)
            st.write("Router Agent: Classifying Document...")
            doc_type = "Insurance"
            lower_text = policy_text.lower()[:2000] # Check first 2000 chars
            
            if any(x in lower_text for x in ["rent", "lease", "tenant", "landlord", "license fee"]):
                doc_type = "Rent"
                st.info("📂 Detected: Rental Agreement. Activating **Tenant Guardian**.")
            elif any(x in lower_text for x in ["employment", "offer letter", "salary", "compensation", "probation"]):
                doc_type = "Job"
                st.info("📂 Detected: Offer Letter. Activating **Career Shield**.")
            else:
                st.info("📂 Detected: Insurance Policy. Activating **Auditor Agent**.")

            # 2. Specialist Agent Activation
            report = {}
            if doc_type == "Rent":
                st.write("Tenant Guardian: Analyzing Lease Terms...")
                from agents.tenant_guardian import TenantGuardianAgent
                guardian = TenantGuardianAgent()
                raw_report = guardian.audit_rent_agreement(policy_text)
                # Map to generic keys for UI
                report = {
                    "risk_score": 100 - raw_report.get("risk_score", 50), # Invert score (High Fairness = Low Risk)
                    "risk_reason": raw_report.get("risk_reason"),
                    "room_rent": raw_report.get("lock_in"),
                    "co_pay": raw_report.get("security_deposit"),
                    "waiting_periods": raw_report.get("notice_period"),
                    "sub_limits": raw_report.get("maintenance"),
                    "exclusions": [raw_report.get("eviction_terms")]
                }
                
            elif doc_type == "Job":
                st.write("Career Shield: Analyzing Offer Letter...")
                from agents.career_shield import CareerShieldAgent
                shield = CareerShieldAgent()
                raw_report = shield.audit_offer_letter(policy_text)
                # Map to generic keys for UI
                report = {
                    "risk_score": 100 - raw_report.get("risk_score", 50), # Invert score
                    "risk_reason": raw_report.get("risk_reason"),
                    "room_rent": raw_report.get("bond"),
                    "co_pay": raw_report.get("notice_period"),
                    "waiting_periods": raw_report.get("non_compete"),
                    "sub_limits": raw_report.get("variable_pay"),
                    "exclusions": [raw_report.get("ip_rights")]
                }
                
            else:
                st.write("Auditor Agent: Scanning Clauses...")
                from agents.auditor import AuditorAgent
                auditor = AuditorAgent()
                report = auditor.audit_policy(policy_text) # Default Insurance Audit

            st.session_state.audit_report = report
            
            # 3. Sentinel Agent
            st.write("Sentinel Agent: Checking Reputation...")
            from agents.sentinel import SentinelAgent
            sentinel = SentinelAgent()
            # Mock extraction for demo
            reputation = sentinel.check_reputation("Star Health") 
            st.session_state.reputation = reputation
            
            # 4. Architect Agent (Financials)
            st.write("Architect Agent: Forecasting Value...")
            from agents.architect import ArchitectAgent
            architect = ArchitectAgent()
            fig = architect.forecast_financials(500000)
            st.session_state.financial_fig = fig
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)
        
        # Log Data (Anonymous)
        log_market_intel({
            "company_name": "Unknown", # In a real app, extract this from text
            "risk_score": report.get("risk_score", 0)
        })
        
        st.session_state.processing_complete = True

    # --- The Auto-Report Dashboard ---
    if st.session_state.processing_complete:
        report = st.session_state.audit_report
        
        # Glass Container for Report
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        # Top Row: Risk Score & Reputation
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            score = report.get('risk_score', 0)
            color = "#ff4b4b" if score > 70 else "#ffa500" if score > 30 else "#00cc66"
            st.markdown(f"<h2 style='color: {color}; margin:0;'>{score}/100</h2>", unsafe_allow_html=True)
            st.caption("Risk Score")
        with c2:
            st.metric("Market Sentiment", "Neutral", "⚠️ Complaints Found")
        with c3:
            st.markdown(f"**Critical Alert**: {report.get('risk_reason', 'N/A')}")
            
        st.divider()
        
        # Middle Row: Clauses
        k1, k2, k3 = st.columns(3)
        with k1:
            st.error(f"**Room Rent**: {report.get('room_rent')}")
        with k2:
            st.warning(f"**Co-Pay**: {report.get('co_pay')}")
        with k3:
            st.info(f"**Waiting**: {report.get('waiting_periods')}")
            
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Chat Interface ---
        st.markdown("### 💬 Ask PolicyPARAKH")
        
        # Display History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("Ask about a clause, or type 'Compare' to find better options..."):
            
            # --- God Mode Check ---
            if prompt.strip() == "/godmode":
                st.session_state.admin_revealed = True
                st.toast("🔓 God Mode Enabled: Admin Access Revealed in Sidebar!")
                time.sleep(1)
                st.rerun()
            
            # User Message
            # User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Simple Router for Demo
                    response = ""
                    if "compare" in prompt.lower():
                        from agents.scout import ScoutAgent
                        scout = ScoutAgent()
                        response = scout.compare_policies("Current Policy", memory.get_profile_string())
                    elif "genesis" in prompt.lower():
                        from agents.genesis import GenesisAgent
                        gen = GenesisAgent()
                        response = gen.solve_problem(prompt)
                    else:
                        # Default to Gemini Chat
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=security.get_next_api_key())
                        # Inject Context
                        context_prompt = f"Context: {st.session_state.policy_text[:5000]}\n\nUser Question: {prompt}"
                        response = llm.invoke(context_prompt).content
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Courtroom Overlay ---
# --- Courtroom Overlay ---
if st.session_state.get("show_courtroom"):
    st.markdown("---")
    st.subheader("⚖️ Virtual Courtroom")
    
    from agents.lawyer import CourtroomAgent
    court = CourtroomAgent()
    
    # Interview Phase
    if "interview_q" not in st.session_state:
        st.session_state.interview_q = court.conduct_interview(st.session_state.get("policy_text", ""))
    
    # Chat-style Interview
    with st.chat_message("assistant", avatar="👨‍⚖️"):
        st.write(f"**Lawyer**: {st.session_state.interview_q}")
        
    user_response = st.chat_input("Answer the lawyer...", key="court_answer_input")
    
    if user_response:
        # 1. Gather Witness Data
        with st.spinner("Subpoenaing Witnesses (Architect & Sentinel)..."):
            # Mock data fetching for demo speed - in prod, call agents
            architect_data = "Inflation will reduce cover value by 40% in 5 years."
            sentinel_data = "Company has 1500+ consumer complaints regarding claim rejection."
            
        with st.spinner("The Jury is assembling..."):
            full_scenario = f"{st.session_state.get('scenario', 'General Dispute')}. User Fact: {user_response}"
            
            # Call Cinematic Lawyer
            case_data = court.simulate_argument(
                st.session_state.get("policy_text", ""), 
                full_scenario,
                architect_data,
                sentinel_data
            )
            
            # Save to Memory
            memory.add_case_history({
                "scenario": full_scenario,
                "verdict": case_data.get("verdict"),
                "timestamp": time.time()
            })
            
            # Cinematic Playback UI
            st.markdown("### 🎬 Courtroom Drama")
            script_container = st.container()
            
            for line in case_data.get("script", []):
                time.sleep(1.5) # Cinematic delay
                with script_container:
                    speaker = line["speaker"]
                    text = line["text"]
                    msg_type = line.get("type", "text")
                    
                    if msg_type == "judge":
                        st.markdown(f"**👨‍⚖️ {speaker}**: {text}")
                    elif msg_type == "prosecution":
                        st.error(f"**👹 {speaker}**: {text}")
                    elif msg_type == "defense":
                        st.info(f"**🛡️ {speaker}**: {text}")
                    elif msg_type == "witness":
                        st.warning(f"**🙋 {speaker}**: {text}")
                    elif msg_type == "action":
                        st.caption(f"*{text}*")
            
            st.divider()
            
            # Verdict & SWOT
            verdict = case_data.get("verdict", {})
            swot = case_data.get("swot", {})
            
            v_col1, v_col2 = st.columns([2, 1])
            with v_col1:
                st.success(f"**Final Verdict**: {verdict.get('winner')} ({verdict.get('probability')})")
                st.write(f"*{verdict.get('summary')}*")
            with v_col2:
                st.markdown("**SWOT Analysis**")
                st.write(f"✅ **Strengths**: {', '.join(swot.get('strengths', []))}")
                st.write(f"❌ **Weaknesses**: {', '.join(swot.get('weaknesses', []))}")
            
            if st.button("End Session"):
                st.session_state.show_courtroom = False
                del st.session_state.interview_q
                st.rerun()
