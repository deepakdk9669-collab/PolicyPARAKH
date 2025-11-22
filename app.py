import streamlit as st
import time
import random
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain_community.tools import DuckDuckGoSearchRun

# --- 1. CONFIGURATION (Gemini Look) ---
st.set_page_config(
    page_title="PolicyPARAKH AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GEMINI-STYLE CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #131314; color: #E3E3E3; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20;
        border-right: 1px solid #333;
    }
    
    /* Chat Input at Bottom */
    .stChatInput {
        position: fixed;
        bottom: 20px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2C2C2E; color: white; 
        border-radius: 20px; border: none; padding: 10px 20px;
    }
    .stButton>button:hover { background-color: #444746; }
    
    /* User/AI Bubbles */
    div[data-testid="user-message"] {
        background-color: #2C2C2E; color: white; border-radius: 15px; padding: 15px;
    }
    div[data-testid="assistant-message"] {
        background-color: #131314; color: white; padding: 15px;
    }
    
    /* Profile Card in Sidebar */
    .profile-card {
        background: #2C2C2E; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC CORE ---

def rotate_key():
    try:
        keys = st.secrets["API_KEYS"]
        if isinstance(keys, list): genai.configure(api_key=random.choice(keys))
        else: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except: pass

def search_web(query):
    """Safe Search that handles errors"""
    try:
        search = DuckDuckGoSearchRun()
        return search.invoke(f"{query} insurance scam reviews reddit")
    except:
        return "⚠️ Network Offline: Could not verify online reputation."

def analyze_doc(text, profile_context):
    rotate_key()
    
    # --- MODEL SELECTION (FORCING 2.5 PRO) ---
    # We try the standard alias first. If it fails, we fallback to experimental.
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro') 
    except:
        # Fallback if the name is slightly different in your region
        model = genai.GenerativeModel('models/gemini-2.5-pro-preview-05-06')
    
    prompt = f"""
    ACT AS: PolicyPARAKH, an elite Legal AI (Powered by Gemini 2.5 Pro).
    
    USER PROFILE (Crucial Context):
    {profile_context}
    
    DOCUMENT TEXT:
    {text[:45000]} 
    
    TASK:
    1. Identify the Document Type.
    2. Audit it specifically against the User's Profile (e.g., if user has Parents, check Age limits).
    3. Give a Risk Score (0-100).
    4. List 3 Critical Red Flags.
    
    OUTPUT: Keep it conversational and direct. Use Bold text for emphasis.
    """
    return model.generate_content(prompt).text

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am PolicyPARAKH (Gemini 2.5 Pro Edition). Upload a document or update your Family Profile in the sidebar to get started."}]
if "history_list" not in st.session_state:
    st.session_state.history_list = ["New Chat"]
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"Name": "User", "Age": "25", "Family": "None"}

# --- 5. SIDEBAR (HISTORY & SETTINGS) ---
with st.sidebar:
    st.title("✨ PolicyPARAKH")
    st.caption("Model: Gemini 2.5 Pro")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Ready for a new analysis. Upload a file or ask a question."}]
        st.rerun()
    
    st.markdown("### 🕒 Recent")
    for i, chat in enumerate(st.session_state.history_list):
        st.caption(f"💬 {chat}")

    st.markdown("---")
    
    # PROFILE SETTINGS
    with st.expander("👤 My Family Profile", expanded=True):
        st.markdown("AI will use this to find personalized risks.")
        name = st.text_input("Your Name", st.session_state.user_profile["Name"])
        age = st.text_input("Your Age", st.session_state.user_profile["Age"])
        family = st.text_area("Family Details (e.g., Mom 65yr diabetic)", st.session_state.user_profile["Family"])
        
        if st.button("Save Profile"):
            st.session_state.user_profile = {"Name": name, "Age": age, "Family": family}
            st.success("Profile Updated!")

# --- 6. MAIN CHAT INTERFACE ---

# File Uploader acts as an "Attachment" button
uploaded_file = st.file_uploader("📎 Attach Policy/Bill (PDF)", type="pdf", label_visibility="collapsed")

if uploaded_file:
    # Process PDF immediately upon upload if not already processed
    last_msg = st.session_state.messages[-1]["content"]
    if "Analysis Complete" not in last_msg and "Risk Score" not in last_msg:
        with st.chat_message("assistant"):
            with st.spinner("Reading document & applying Family Context (Gemini 2.5 Pro)..."):
                pdf = PdfReader(uploaded_file)
                text = ""
                for page in pdf.pages: text += page.extract_text() or ""
                
                # Build Context String
                prof = st.session_state.user_profile
                context_str = f"User: {prof['Name']}, Age: {prof['Age']}, Family History: {prof['Family']}"
                
                try:
                    # Run Analysis
                    analysis = analyze_doc(text, context_str)
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": analysis})
                    
                    # Update Sidebar History Name
                    if len(st.session_state.history_list) < 5:
                        st.session_state.history_list.insert(0, "Policy Audit #" + str(random.randint(100,999)))
                except Exception as e:
                    st.error(f"⚠️ Gemini 2.5 Pro Error: {str(e)}")
                    st.info("Tip: If this fails, Google might have restricted Pro access on your free key. Consider switching back to Flash.")
                
        st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input (Fixed at Bottom)
if prompt := st.chat_input("Ask follow-up questions..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rotate_key()
            
            # TRYING 2.5 PRO FOR CHAT TOO
            try:
                model = genai.GenerativeModel('models/gemini-2.5-pro')
            except:
                model = genai.GenerativeModel('models/gemini-1.5-flash') # Backup
            
            # Smart Search Trigger
            scam_context = ""
            if "scam" in prompt.lower() or "review" in prompt.lower() or "fraud" in prompt.lower():
                status_box = st.status("🕵️ Sentinel searching dark web...", expanded=False)
                scam_context = search_web(prompt)
                status_box.update(label="Search Complete", state="complete")
            
            # Reply
            full_prompt = f"""
            CHAT HISTORY: {st.session_state.messages[-3:]}
            USER PROFILE: {st.session_state.user_profile}
            SEARCH INTEL: {scam_context}
            USER QUERY: {prompt}
            
            Answer directly.
            """
            try:
                response = model.generate_content(full_prompt).text
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
    
