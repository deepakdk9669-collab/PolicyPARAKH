import streamlit as st
import utils
import auditor
import critic
import sentinel
import architect
import courtroom
import market_scout
import uuid
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="PolicyPARAKH SuperApp", layout="wide", initial_sidebar_state="expanded")

# --- CSS FOR IMMERSIVE UI ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    
    /* Gem Card Styling in Sidebar */
    .gem-button {
        width: 100%;
        background-color: #1F6FEB;
        color: white;
        padding: 10px;
        border-radius: 8px;
        border: none;
        text-align: left;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .gem-button:hover { background-color: #58A6FF; cursor: pointer; }
    
    /* Chat Input Floating */
    .stChatInput { position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem; background: #0E1117; z-index: 999; }
    
    /* Courtroom Specific Styles */
    .court-box { border: 1px solid #30363D; padding: 20px; border-radius: 10px; background-color: #161B22; }
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

# --- FUNCTIONS ---
def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def add_message(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

# ========================================================
# SIDEBAR (NAVIGATION)
# ========================================================
with st.sidebar:
    # HOME BUTTON
    if st.button("🏠 Home (Chat & Tools)", use_container_width=True, type="secondary" if st.session_state.page == "home" else "primary"):
        switch_page("home")
    
    st.divider()
    
    # GEMS SECTION (Dedicated Apps)
    st.markdown("### 💎 Gems")
    # Using a cleaner look for the Gem
    if st.button("⚖️ Courtroom Simulator", use_container_width=True):
        switch_page("courtroom")
    
    st.divider()
    
    # PROFILE
    with st.expander("👤 Family Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Dad (Heart Patient)")

# ========================================================
# PAGE 1: HOME (Chat + Tools like Market Scout)
# ========================================================
if st.session_state.page == "home":
    st.markdown("### PolicyPARAKH <span style='color:#58a6ff'>AI</span>", unsafe_allow_html=True)
    
    # 1. UPLOAD AREA (Integrated)
    if 'auditor_report' not in st.session_state:
        with st.container():
            uploaded_file = st.file_uploader("📎 Upload Policy (PDF/Image)", type=["pdf", "png", "jpg"], label_visibility="collapsed")
            client = utils.initialize_gemini()
            
            if uploaded_file and client:
                if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
                    with st.spinner("Processing..."):
                        # Mime Type Logic
                        file_type = uploaded_file.type
                        mime = "application/pdf" if file_type == "application/pdf" else file_type
                        if mime == "application/pdf": data = utils.base64_encode_pdf(uploaded_file)
                        else: import base64; data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                        
                        # Store
                        st.session_state.file_data = data
                        st.session_state.file_mime = mime
                        st.session_state.current_file_name = uploaded_file.name
                        
                        # Audit
                        report = auditor.generate_risk_assessment(client, "Scan this.", data, mime)
                        if report:
                            st.session_state.auditor_report = report
                            # Run Critic
                            reviewed_report = critic.review_report(client, report, "Check this.")
                            st.session_state.auditor_report = reviewed_report
                            
                            add_message("assistant", f"✅ **Analyzed:** {reviewed_report.get('summary')}")
                            st.rerun()

    # 2. CHAT HISTORY
    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # 3. CHAT INPUT (With Tool Routing)
    if prompt := st.chat_input("Ask 'Compare with Market', 'Check Reviews', or 'Explain'"):
        add_message("user", prompt)
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.markdown("🧠 *Thinking...*")
            
            client = utils.initialize_gemini()
            context = st.session_state.get('auditor_report', {})
            
            # --- TOOL ROUTING LOGIC (Market Scout is HERE) ---
            prompt_lower = prompt.lower()
            
            # Tool 1: Market Scout (Comparison)
            if any(x in prompt_lower for x in ["compare", "better", "alternative", "market"]):
                if context:
                    res = market_scout.compare_policy(client, context)
                else:
                    res = "Please upload a policy first for comparison."
            
            # Tool 2: Sentinel (Reviews/Scam/Location)
            elif any(x in prompt_lower for x in ["scam", "review", "gwalior", "location", "rating"]):
                if "gwalior" in prompt_lower or "location" in prompt_lower:
                    # Local Check
                    res = market_scout.check_local_presence(client, context.get('entity_name', 'This Company'), "Gwalior")
                else:
                    # Sentiment Check
                    res = market_scout.get_social_sentiment(client, context.get('entity_name', 'This Company'))
            
            # Tool 3: Architect (Inflation)
            elif "value" in prompt_lower or "inflation" in prompt_lower:
                 df = architect.architect_agent_forecast(client, {})
                 st.session_state.architect_data = df
                 res = "Inflation Forecast Chart Generated."
                 st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])
            
            # Default: General Chat with Internet
            else:
                import tavily_search
                web_context = tavily_search.tavily_deep_search(prompt)
                full_prompt = f"Context: {context}\nWeb Info: {web_context}\nUser: {prompt}"
                
                try:
                    api_res = client.models.generate_content(model='gemini-2.5-pro', contents=full_prompt)
                    res = api_res.text
                except:
                    res = "Connection Error."

            response_placeholder.markdown(res)
            add_message("assistant", res)

# ========================================================
# PAGE 2: COURTROOM SIMULATOR (The Gem - Dedicated App)
# ========================================================
elif st.session_state.page == "courtroom":
    st.markdown("### ⚖️ Virtual Courtroom <span style='font-size:0.8rem; color:gray'>(Simulator Mode)</span>", unsafe_allow_html=True)
    
    # Back Button
    if st.button("← Exit Simulation"):
        switch_page("home")
    
    st.info("💡 **Tip:** Provide 'Secret Clues' (e.g., 'I have a video of the doctor') to help your AI Advocate win.")

    # Dedicated Courtroom History
    if "court_history" not in st.session_state: 
        st.session_state.court_history = [{"role": "assistant", "content": "I am the Judge. Present your case. What is the claim rejection reason?"}]

    # Display Court Transcript
    for msg in st.session_state.court_history:
        avatar = "⚖️" if msg['role'] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Dedicated Input for Court
    if claim_input := st.chat_input("State your claim/argument..."):
        st.session_state.court_history.append({"role": "user", "content": claim_input})
        with st.chat_message("user", avatar="👤"): st.markdown(claim_input)
        
        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("👨‍⚖️ Reviewing Case Laws & Arguments..."):
                client = utils.initialize_gemini()
                policy_context = st.session_state.get('auditor_report', "No Policy Uploaded")
                
                # Call the Simulator
                verdict = courtroom.run_courtroom_simulation(client, policy_context, claim_input, claim_input)
                
                st.markdown(verdict)
                st.session_state.court_history.append({"role": "assistant", "content": verdict})
