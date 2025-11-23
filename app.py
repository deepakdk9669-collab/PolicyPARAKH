import streamlit as st
import time
import random
import json
import re
from PyPDF2 import PdfReader
import google.generativeai as genai
from duckduckgo_search import DDGS
import plotly.graph_objects as go

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="PolicyPARAKH",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GEMINI NATIVE CSS (THE LOOK) ---
st.markdown("""
<style>
    /* 1. Main Background (Deep Gemini Grey) */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
        font-family: 'Roboto', sans-serif;
    }
    
    /* 2. Sidebar (Lighter Grey) */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20;
        border-right: 1px solid #333;
    }
    
    /* 3. Chat Input (Fixed Bottom Pill) */
    .stChatInput {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 70%;
        z-index: 1000;
    }
    .stChatInput input {
        background-color: #2C2C2E;
        color: white;
        border-radius: 25px;
        border: 1px solid #444;
    }
    
    /* 4. User Message (Grey Bubble, Right Aligned) */
    div[data-testid="user-message"] {
        background-color: #2C2C2E;
        color: #F1F1F1;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin-left: auto;
        max-width: 70%;
        font-size: 15px;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    
    /* 5. AI Message (Transparent, Left Aligned, Gemini Icon) */
    div[data-testid="assistant-message"] {
        background-color: transparent;
        color: #E3E3E3;
        padding: 0px;
        max-width: 100%;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* 6. Hide Streamlit Header */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 7. Suggestion Chips (Buttons) */
    .stButton>button {
        background-color: #1E1F20;
        color: #A8C7FA;
        border: 1px solid #444;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 14px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #2C2C2E;
        border-color: #A8C7FA;
    }
    
    /* 8. History List Styling */
    .history-item {
        padding: 10px;
        color: #E3E3E3;
        cursor: pointer;
        border-radius: 5px;
        font-size: 14px;
    }
    .history-item:hover { background-color: #333; }

</style>
""", unsafe_allow_html=True)

# --- 3. INTELLIGENCE CORE ---

def rotate_key():
    try:
        keys = st.secrets["API_KEYS"]
        if isinstance(keys, list): genai.configure(api_key=random.choice(keys))
        else: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except: pass

def get_gemini_response(prompt, context, mode="AUDITOR"):
    rotate_key()
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash') # Using Flash for Speed
        
        sys_prompt = "You are PolicyPARAKH, a specialized Legal AI."
        if mode == "LAWYER":
            sys_prompt = "You are a Stubborn Insurance Lawyer. Your goal is to reject claims."
        
        full_prompt = f"""
        {sys_prompt}
        CONTEXT: {context[:40000]}
        USER QUERY: {prompt}
        INSTRUCTION: Use Markdown. Be structured. Use tables for data.
        """
        return model.generate_content(full_prompt).text
    except Exception as e:
        return "⚠️ I am unable to connect to the neural core right now."

def get_inflation_chart():
    years = [2025, 2028, 2031, 2034]
    cost = [15000, 22000, 35000, 55000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=cost, mode='lines+markers', name='Premium', line=dict(color='#ff8a80', width=3)))
    fig.update_layout(
        title="📉 Projected Premium Inflation",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        font=dict(family="Roboto", color="#E3E3E3")
    )
    return fig

def get_sentinel_data(query):
    try:
        res = DDGS().text(f"{query} scam reviews reddit", max_results=2)
        return "\n".join([f"> *{r['body'][:100]}...*" for r in res])
    except: return "No specific alerts found."

# --- 4. SESSION STATE (HISTORY MANAGEMENT) ---
if "chat_history" not in st.session_state:
    # Pre-filling some fake history to show the UI feature
    st.session_state.chat_history = [
        {"title": "HDFC Ergo Policy Audit", "id": 1},
        {"title": "Jio Fiber Bill Check", "id": 2},
        {"title": "LIC Jeevan Anand Analysis", "id": 3}
    ]
if "messages" not in st.session_state:
    st.session_state.messages = [] # Current chat messages
if "full_text" not in st.session_state: st.session_state.full_text = ""
if "profile" not in st.session_state: st.session_state.profile = {}

# --- 5. SIDEBAR (GEMINI NAV) ---
with st.sidebar:
    st.markdown("## ✨ PolicyPARAKH")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_text = ""
        st.rerun()
    
    st.markdown("### Recent")
    # Rendering History List
    for chat in st.session_state.chat_history:
        st.markdown(f"<div class='history-item'>💬 {chat['title']}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("👤 Family Context", expanded=True):
        name = st.text_input("Name")
        details = st.text_area("Medical History", placeholder="e.g. Mom 65yr Diabetic")
        if st.button("Update Memory"):
            st.session_state.profile = {"Name": name, "Details": details}
            st.success("Saved")

# --- 6. MAIN CHAT AREA ---

# WELCOME SCREEN (If no chat yet)
if not st.session_state.messages and not st.session_state.full_text:
    c1, c2 = st.columns([0.1, 0.9])
    with c1: st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=50)
    with c2: 
        st.markdown("### Hello, Human.")
        st.markdown("<span style='color:#6c757d'>How can I help you audit your documents today?</span>", unsafe_allow_html=True)
    
    # File Upload in Main Area (Like Gemini's Image Upload)
    uploaded_file = st.file_uploader("Upload Policy / Bill (PDF)", type="pdf", label_visibility="collapsed")
    
    # Suggestion Chips
    col1, col2, col3 = st.columns(3)
    with col1: st.button("🛡️ Is my data safe?", use_container_width=True)
    with col2: st.button("📉 Predict future costs", use_container_width=True)
    with col3: st.button("⚖️ Simulate Court Battle", use_container_width=True)

    if uploaded_file:
        with st.spinner("⚙️ Analyzing Document Structure..."):
            pdf = PdfReader(uploaded_file)
            text = ""
            for page in pdf.pages: text += page.extract_text() or ""
            st.session_state.full_text = text
            
            # Initial Audit
            st.session_state.messages.append({"role": "user", "content": "Audit this document."})
            
            # Sentinel Check
            intel = get_sentinel_data("Insurance Company")
            
            analysis = get_gemini_response(f"Audit this. Profile: {st.session_state.profile}. Include Risk Score, Verdict, and 3 Red Flags. Sentinel Data: {intel}", text)
            
            st.session_state.messages.append({"role": "assistant", "content": analysis})
            
            # Add to History Sidebar
            st.session_state.chat_history.insert(0, {"title": "New Policy Scan", "id": random.randint(100,999)})
            st.rerun()

# CHAT STREAM
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Render special elements if tagged
            if msg.get("type") == "graph":
                st.plotly_chart(get_inflation_chart(), use_container_width=True)

    # Input Area
    if prompt := st.chat_input("Ask about coverage, clauses, or hidden fees..."):
        # User
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Assistant
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                
                # 1. COURTROOM TRIGGER
                if "court" in prompt.lower() or "fight" in prompt.lower():
                    response = get_gemini_response(prompt, st.session_state.full_text, mode="LAWYER")
                    st.markdown("⚖️ **LAWYER MODE ACTIVE**")
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                # 2. TIME MACHINE TRIGGER
                elif "future" in prompt.lower() or "cost" in prompt.lower() or "inflation" in prompt.lower():
                    st.markdown("Here is the **10-Year Financial Projection** based on Age Banding clauses:")
                    st.plotly_chart(get_inflation_chart(), use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": "Here is the projection:", "type": "graph"})
                
                # 3. NORMAL AUDIT
                else:
                    response = get_gemini_response(prompt, st.session_state.full_text)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

