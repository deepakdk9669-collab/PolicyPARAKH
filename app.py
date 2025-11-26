import streamlit as st
import utils
import auditor
import critic
import sentinel
import architect
import courtroom
import market_scout
import search_engine
import uuid
import base64

st.set_page_config(page_title="PolicyPARAKH AI", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Google Sans', sans-serif; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .stChatInput { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 60%; z-index: 1000; background-color: #1E1F20; border-radius: 25px; border: 1px solid #444; }
    .gem-btn { display: block; width: 100%; padding: 10px; margin: 5px 0; background: #28292A; color: white; border-radius: 10px; text-align: left; border: 1px solid #333; transition: 0.3s; }
    .gem-btn:hover { background: #3C4043; border-color: #58a6ff; cursor: pointer; }
    @media (max-width: 768px) { .stChatInput { width: 90%; left: 5%; transform: none; } }
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "home"
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

def navigate(page): st.session_state.page = page; st.rerun()
def new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
    if 'auditor_report' in st.session_state: del st.session_state.auditor_report
    navigate("home")
def add_msg(role, content): st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"): new_chat()
    st.markdown("### Gems")
    if st.button("⚖️ Courtroom Simulator", help="Enter Virtual Court"): navigate("courtroom")
    if st.button("🛒 Scout (Tool)", help="Use in Home Chat"): navigate("home")
    with st.expander("👤 Family Profile"):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile)

if st.session_state.page == "home":
    uploader_state = 'collapsed' if 'auditor_report' in st.session_state else 'expanded'
    with st.expander("📎 Upload Document (PDF/Image/Video)", expanded=(uploader_state=='expanded')):
        uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg", "mp4", "mp3"], label_visibility="collapsed")
    
    client = utils.initialize_gemini()
    if uploaded_file and client:
        if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing..."):
                ft = uploaded_file.type
                mime = "application/pdf" if "pdf" in ft else (ft if "image" in ft else ("video/mp4" if "video" in ft else "application/pdf"))
                data = uploaded_file.getvalue() if "pdf" not in mime else utils.base64_encode_pdf(uploaded_file)
                if "pdf" not in mime: 
                    import base64
                    # For non-pdf binary data, we need to handle it appropriately or pass raw bytes if auditor accepts it. 
                    # Assuming auditor accepts raw bytes for image/video now or we encode it.
                    # Let's use the utils function for consistency if it handles bytes, 
                    # but here we just pass the raw bytes if auditor.py is updated to handle it.
                    pass 

                st.session_state.file_data = data
                st.session_state.current_file_name = uploaded_file.name
                
                # Note: Ensure auditor.py handles raw bytes for image/video as per previous updates
                report = auditor.generate_risk_assessment(client, "Audit", data, mime)
                if report:
                    st.session_state.auditor_report = report
                    add_msg("assistant", f"✅ **Analysis Complete:** {report.get('summary')}")
                    st.rerun()

    for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    audio_val = st.audio_input("🎙️") 
    prompt = st.chat_input("Ask 'Compare', 'Review', or 'Explain'")
    user_input = "Audio received" if audio_val else (prompt if prompt else None)

    if user_input:
        add_msg("user", user_input)
        if audio_val: with st.chat_message("user"): st.markdown(user_input)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            client = utils.initialize_gemini()
            context = st.session_state.get('auditor_report', {})
            prompt_lower = user_input.lower()
            
            if "compare" in prompt_lower: res = market_scout.compare_policy(client, context)
            elif any(x in prompt_lower for x in ["scam", "review", "location"]): res = market_scout.get_social_sentiment(client, context.get('entity_name','Company'))
            elif "court" in prompt_lower: res = "Please switch to 'Courtroom Mode' from Sidebar."
            else:
                web = search_engine.search_web(user_input)
                try: res = client.models.generate_content(model='gemini-2.5-pro', contents=f"Context:{context}\nWeb:{web}\nUser:{user_input}").text
                except: res = "Error."
            
            placeholder.markdown(res)
            add_msg("assistant", res)
            if audio_val: st.rerun()

elif st.session_state.page == "courtroom":
    st.title("⚖️ Courtroom Simulator")
    if st.button("← Back"): navigate("home")
    if claim := st.chat_input("State your claim..."):
        with st.chat_message("user"): st.markdown(claim)
        with st.chat_message("assistant"):
            with st.spinner("Fighting..."):
                client = utils.initialize_gemini()
                context = st.session_state.get('auditor_report', "No Policy")
                res = courtroom.run_courtroom_simulation(client, context, claim, claim)
                st.markdown(res)
