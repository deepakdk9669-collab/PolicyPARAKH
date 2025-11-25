import streamlit as st
import utils
import auditor
import sentinel
import architect
import courtroom
import market_scout
import uuid
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="PolicyPARAKH Ultimate", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Chat Input Styling to look like a floating bar */
    .stChatInput { position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem; background: #0E1117; z-index: 999; }
    
    /* Custom File Uploader to look cleaner */
    [data-testid="stFileUploader"] {
        padding: 10px;
        border: 1px dashed #4f46e5;
        border-radius: 10px;
        background-color: #1e293b;
    }
    
    /* Badges */
    .gem-badge { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .doc-badge { background-color: #2ea043; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "sessions" not in st.session_state: 
    st.session_state.sessions = {} 

if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id

if "family_profile" not in st.session_state: 
    st.session_state.family_profile = ""

# --- HELPER FUNCTIONS ---
def add_message(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    # Clear document context for new chat
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    if 'file_data' in st.session_state: del st.session_state.file_data

# --- SIDEBAR (Navigation & Profile) ---
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()
    
    st.divider()
    
    with st.expander("👤 My Profile (Family Card)", expanded=True):
        st.caption("AI will cross-reference policies with this info.")
        st.session_state.family_profile = st.text_area(
            "Details", 
            value=st.session_state.family_profile, 
            placeholder="Ex: Mom (65, Diabetes), Dad (Smoker), Me (Freelancer)",
            height=100,
            label_visibility="collapsed"
        )

    st.subheader("💎 God Mode Tools")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚖️ Courtroom"):
            add_message("system", "🔥 **Courtroom Mode Activated!** I am acting as your Lawyer. What is your claim?")
            st.rerun()
    with col2:
        if st.button("🛒 Market Scout"):
            client = utils.initialize_gemini()
            if 'auditor_report' in st.session_state and client:
                res = market_scout.compare_policy(client, st.session_state.auditor_report)
                add_message("assistant", res)
            else:
                st.toast("⚠️ Upload a document first to compare!")
            st.rerun()

    st.divider()
    st.subheader("🕒 Recent Chats")
    # Show last 5 chats
    for sess_id, data in list(st.session_state.sessions.items())[::-1][:5]:
        if st.button(f"💬 {data.get('title', 'Chat')}", key=sess_id, use_container_width=True):
            st.session_state.current_session_id = sess_id
            st.rerun()

# --- MAIN CONTENT AREA ---
st.markdown(f"### PolicyPARAKH <span class='gem-badge'>Ultimate</span>", unsafe_allow_html=True)

# 1. Combined Upload Area (Collapsible to save space after upload)
uploader_expanded = 'auditor_report' not in st.session_state
with st.expander("📎 Attach Document (Insurance / Contract / Loan)", expanded=uploader_expanded):
    uploaded_file = st.file_uploader("Drag & Drop PDF or Image", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

client = utils.initialize_gemini()

# 2. Document Processing Logic
if uploaded_file and client:
    # Check if this is a new file to process
    if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        with st.spinner("🧠 Analyzing Document Structure..."):
            
            # Determine Mime Type
            file_type = uploaded_file.type
            if file_type == "application/pdf": 
                mime = "application/pdf"
            elif file_type in ["image/png", "image/jpeg", "image/jpg"]: 
                mime = file_type
            else: 
                mime = "application/pdf" # Fallback
            
            # Encode Data
            if mime == "application/pdf": 
                data = utils.base64_encode_pdf(uploaded_file)
            else: 
                data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            
            # Store in Session
            st.session_state.file_data = data
            st.session_state.file_mime = mime
            st.session_state.current_file_name = uploaded_file.name
            
            # Run Universal Auditor
            report = auditor.generate_risk_assessment(client, "Deep Scan this document.", data, mime)
            
            if report:
                st.session_state.auditor_report = report
                
                # Extract Universal Fields safely
                doc_type = report.get('doc_type', 'Document')
                entity = report.get('entity_name', 'Unknown Entity')
                score = report.get('risk_score_0_to_100', 'N/A')
                bad_clauses = report.get('bad_clauses', 'None detected.')
                good_points = report.get('good_points', 'None detected.')
                summary = report.get('summary', 'No summary available.')
                
                # Generate a nice summary card in the chat
                msg = f"""
                ✅ **Analysis Complete: {doc_type}** <span class='doc-badge'>{score}/100 Risk</span>
                
                **Entity:** {entity}
                
                🚩 **Critical Risks/Loopholes:**
                {bad_clauses}
                
                💚 **Positive Clauses:**
                {good_points}
                
                **Verdict:** {summary}
                """
                add_message("assistant", msg)
                
                # Auto-Family Check (If profile exists)
                if st.session_state.family_profile:
                    fam_check = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=f"Document Context: {summary}. Risks: {bad_clauses}. Family Profile: {st.session_state.family_profile}. Cross-reference and warn me if my family is affected."
                    )
                    add_message("assistant", f"⚠️ **Personalized Family Alert:** {fam_check.text}")
            else:
                add_message("assistant", "⚠️ **Scan Failed:** The document could not be read or the server is busy. Please try again.")
            
            st.rerun()

# 3. Chat Interface (Messages Display)
chat_container = st.container()
with chat_container:
    current_messages = st.session_state.sessions[st.session_state.current_session_id]['messages']
    if not current_messages:
        st.info("👋 Hi! Upload an Insurance Policy, Contract, or Loan Agreement. I will audit it for you.")
    
    for msg in current_messages:
        if msg['role'] == 'system':
            st.warning(msg['content']) # System messages in yellow
        else:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# 4. Chat Input Logic
if prompt := st.chat_input("Ask 'Is this a scam?', 'Find better alternatives', or 'Explain Clause 5'..."):
    add_message("user", prompt)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("Thinking...")
        
        # Build Context
        context = ""
        if 'auditor_report' in st.session_state:
            context = f"[ACTIVE DOCUMENT CONTEXT: {st.session_state.auditor_report}]"
        
        # --- ROUTING LOGIC (The Brain) ---
        prompt_lower = prompt.lower()
        
        # A. Courtroom Mode
        if "court" in prompt_lower or "lawyer" in prompt_lower:
            if 'auditor_report' in st.session_state:
                res = courtroom.run_courtroom_simulation(client, st.session_state.auditor_report, prompt)
            else:
                res = "Please upload a document first to start the legal battle."
        
        # B. Market Scout (Compare)
        elif any(x in prompt_lower for x in ["compare", "better option", "alternative", "market"]):
             if 'auditor_report' in st.session_state:
                res = market_scout.compare_policy(client, st.session_state.auditor_report)
             else:
                res = "Upload a document so I can compare it with the market."
        
        # C. Sentinel (Scam/News Search)
        elif any(x in prompt_lower for x in ["scam", "fraud", "review", "fake", "news"]):
            res = sentinel.sentinel_agent_check(client, st.session_state.get('auditor_report', {}), prompt)
            
        # D. Architect (Inflation/Math)
        elif any(x in prompt_lower for x in ["value", "inflation", "worth", "future"]):
             df = architect.architect_agent_forecast(client, {})
             st.session_state.architect_data = df
             res = "Here is the financial forecast based on current inflation rates:"
             st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])

        # E. General Intelligent Chat (Default)
        else:
            try:
                full_prompt = f"{context}\n\nUser Question: {prompt}"
                # Using 2.5 Pro for high-quality reasoning
                api_res = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=full_prompt
                )
                res = api_res.text
            except Exception as e:
                # Fallback to Flash if Pro is busy
                try:
                    api_res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt
                    )
                    res = api_res.text
                except:
                    res = "I'm having trouble connecting right now. Please try again."

        response_placeholder.markdown(res)
        add_message("assistant", res)
