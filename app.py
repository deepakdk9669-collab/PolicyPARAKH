import streamlit as st
import utils
import auditor
import sentinel
import architect
import courtroom
import market_scout
import uuid

# --- PAGE CONFIG ---
st.set_page_config(page_title="PolicyPARAKH AI", layout="wide", initial_sidebar_state="expanded")

# Styling
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .gem-badge { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .stChatInput { position: fixed; bottom: 0; left: 0; right: 0; padding: 20px; background: #0E1117; z-index: 100; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'title': "New Chat", 'messages': []}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

# --- FUNCTIONS ---
def get_current_messages():
    return st.session_state.sessions[st.session_state.current_session_id]['messages']

def add_message(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

# --- SIDEBAR ---
with st.sidebar:
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {'title': "New Chat", 'messages': []}
        st.session_state.current_session_id = new_id
        if 'auditor_report' in st.session_state: del st.session_state.auditor_report
        st.rerun()
    
    with st.expander("👨‍👩‍👧‍👦 Family Profile"):
        st.session_state.family_profile = st.text_area("Ex: Mom (Diabetes)", value=st.session_state.family_profile)

    st.markdown("### Gems")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚖️ Court"):
            add_message("system", "ACTIVATED: Courtroom Mode. State your claim.")
            st.rerun()
    with c2:
        if st.button("🛒 Scout"):
            client = utils.initialize_gemini()
            if 'auditor_report' in st.session_state and client:
                res = market_scout.compare_policy(client, st.session_state.auditor_report)
                add_message("assistant", res)
                st.rerun()
            else:
                st.toast("Please upload a policy first!")
    
    # History List
    st.markdown("### History")
    for sess_id, sess_data in list(st.session_state.sessions.items())[::-1]:
        if st.button(f"💬 {sess_data['title']}", key=sess_id, use_container_width=True):
            st.session_state.current_session_id = sess_id
            st.rerun()

# --- MAIN UI ---
client = utils.initialize_gemini()
st.markdown(f"### PolicyPARAKH <span class='gem-badge'>2.5 Pro</span>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📎 Add Policy (PDF/Image)", type=["pdf", "png", "jpg"], label_visibility="collapsed")

if uploaded_file:
    if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        with st.spinner("Processing..."):
            # Prepare Data
            if uploaded_file.type == "application/pdf":
                data = utils.base64_encode_pdf(uploaded_file)
            else:
                import base64
                data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            
            st.session_state.file_data = data
            st.session_state.current_file_name = uploaded_file.name
            
            # CRASH PROOF LOGIC: Check if report is valid
            report = auditor.generate_risk_assessment(client, "Scan this.", data)
            
            if report:
                st.session_state.auditor_report = report
                # Use .get() to prevent AttributeError
                score = report.get('risk_score_0_to_100', 'N/A')
                summary = report.get('auditor_summary', 'No summary generated.')
                add_message("assistant", f"📄 **Policy Scanned!**\n\n**Risk Score:** {score}/100\n\n{summary}")
                
                # Family Check with 2.5 Pro
                if st.session_state.family_profile:
                    fam_check = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=f"Policy Risks: {summary}. Family Profile: {st.session_state.family_profile}. Cross-reference and warn me."
                    )
                    add_message("assistant", f"⚠️ **Family Alert:** {fam_check.text}")
            else:
                # If report is None, show error instead of crashing
                add_message("assistant", "⚠️ **Scan Failed:** Server is busy or document is unreadable. Please try again.")

# Chat Display
for msg in get_current_messages():
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask about your policy..."):
    add_message("user", prompt)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        response = "Connecting..."
        
        if "court" in prompt.lower():
            if 'auditor_report' in st.session_state:
                response = courtroom.run_courtroom_simulation(client, st.session_state.auditor_report, prompt)
            else:
                response = "Upload a policy first for the courtroom."
        
        elif any(x in prompt.lower() for x in ["scam", "news"]):
            response = sentinel.sentinel_agent_check(client, st.session_state.get('auditor_report', {}), prompt)
            
        elif "value" in prompt.lower():
             df = architect.architect_agent_forecast(client, {})
             st.session_state.architect_data = df
             response = "Inflation chart generated below."
             st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])

        else:
            # Default Chat with 2.5 Pro
            try:
                context = f"Report: {st.session_state.get('auditor_report')}. User: {prompt}"
                res = client.models.generate_content(model='gemini-2.5-pro', contents=context)
                response = res.text
            except:
                res = client.models.generate_content(model='gemini-2.5-flash', contents=context)
                response = res.text

        st.markdown(response)
        add_message("assistant", response)
