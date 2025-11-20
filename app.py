import streamlit as st
from PyPDF2 import PdfReader
import graph
import time
import google.generativeai as genai

# --- 1. CONFIGURATION (The "Glass Core" Look) ---
st.set_page_config(
    page_title="PolicyPARAKH | Neural Swarm",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional, Technical CSS
st.markdown("""
<style>
    /* Main Background - Dark & Technical */
    .main { background-color: #0A0A0A; color: #E0E0E0; font-family: 'JetBrains Mono', monospace; }
    
    /* The "Terminal" Log Box */
    .agent-log {
        font-family: 'Courier New', monospace;
        background-color: #111;
        color: #00FF41; /* Hacker Green */
        padding: 15px;
        border-radius: 5px;
        border-left: 3px solid #00FF41;
        margin-bottom: 10px;
        font-size: 12px;
    }
    
    /* Chat Bubbles - Distinct & Clean */
    .stChatMessage { background-color: #1A1A1A; border: 1px solid #333; border-radius: 8px; }
    
    /* Headers */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #FAFAFA; }
    .highlight { color: #4F8BF9; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# --- 3. SIDEBAR (The Control Center) ---
with st.sidebar:
    st.title("🧬 Neural Core")
    st.caption("System Status: **ONLINE**")
    
    uploaded_file = st.file_uploader("Ingest Legal Document", type="pdf")
    
    st.markdown("---")
    st.markdown("**Active Agents:**")
    st.markdown("`👁️ Vision` (PDF OCR)")
    st.markdown("`🌐 Sentinel` (Web Search)")
    st.markdown("`⚖️ Judge` (Legal Logic)")
    
    st.markdown("---")
    if st.button("🔴 Reboot System"):
        st.session_state.messages = []
        st.session_state.agent_logs = []
        st.session_state.processing_complete = False
        st.rerun()

# --- 4. MAIN INTERFACE ---

st.title("PolicyPARAKH 🧬")
st.markdown("### Autonomous Legal Audit Swarm")

# A. THE "AGENT EXECUTION" LAYER (Visualizing the Work)
if uploaded_file and not st.session_state.processing_complete:
    
    # Create a container for the "Live" feel
    monitor = st.container()
    
    with monitor:
        st.subheader("⚙️ Swarm Operations")
        
        # Step 1: Ingest
        with st.status("🚀 Initializing Agents...", expanded=True) as status:
            st.write("`[SYSTEM]` Allocating memory...")
            time.sleep(0.5)
            
            # PDF Read
            st.write("`[AGENT: READER]` Extracting text layer...")
            pdf = PdfReader(uploaded_file)
            text = ""
            for page in pdf.pages: text += page.extract_text() or ""
            st.session_state.full_text = text
            st.write(f"`[AGENT: READER]` Successfully extracted {len(text)} tokens.")
            
            # Step 2: Search
            st.write("`[AGENT: SENTINEL]` Identifying entities & scanning web...")
            # We call a helper from graph to get the company name just for the log
            try:
                # Quick extraction for visual feedback
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                entity = model.generate_content(f"Extract entity name: {text[:500]}").text.strip()
                st.write(f"`[AGENT: SENTINEL]` Target Identified: **{entity}**")
                st.write(f"`[AGENT: SENTINEL]` searching: 'Is {entity} legit?'")
            except:
                pass

            # Step 3: Core Audit
            st.write("`[AGENT: JUDGE]` Cross-referencing with legal database...")
            report = graph.run_audit(text) # THE REAL WORK
            
            st.write("`[SYSTEM]` Compiling Final Verdict...")
            status.update(label="✅ Analysis Complete", state="complete", expanded=False)

    # Save result to chat
    st.session_state.messages.append({"role": "assistant", "content": report})
    st.session_state.processing_complete = True
    st.rerun()

# B. THE "CHAT" LAYER (Interaction)
# Split screen: Logs on left (if needed) or just full chat
if st.session_state.processing_complete:
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Advanced Chat Input
    if prompt := st.chat_input("Command the Swarm (e.g., 'Find loopholes', 'Compare with competitors')"):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Visual "Thinking" Indicator
            status_placeholder = st.empty()
            status_placeholder.markdown("`[AGENT: LOGIC]` analyzing query...")
            
            # Logic
            try:
                graph.configure_random_key() # Rotate Keys
                model = genai.GenerativeModel('models/gemini-1.5-pro')
                
                # Advanced System Prompt for Chat
                sys_prompt = f"""
                ACT AS: A Senior Legal Strategist Agent.
                CONTEXT: {st.session_state.full_text[:30000]}
                USER QUERY: {prompt}
                
                MISSION:
                1. If asking for alternatives, search the web for REAL competitors.
                2. If asking for explanation, use analogies.
                3. Be brutally honest about risks.
                """
                
                response = model.generate_content(sys_prompt).text
                
                status_placeholder.empty() # Remove "Thinking"
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                status_placeholder.error(f"Agent Failure: {e}")
                
