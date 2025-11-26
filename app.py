import streamlit as st
import utils
import auditor
import critic  # NEW
import sentinel
import architect
import courtroom
import market_scout
import tavily_search # NEW
import uuid
import base64

# ... (Page Config & CSS same as before) ...
st.set_page_config(page_title="PolicyPARAKH Ultimate", layout="wide", initial_sidebar_state="expanded")
# ... (Keep CSS and Session State logic same as previous app.py) ...

# --- UPDATED SIDEBAR TOOLS ---
with st.sidebar:
    # ... (Keep New Chat & Profile section) ...
    
    st.subheader("💎 God Mode Tools")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚖️ Courtroom"):
            add_message("system", "🔥 Courtroom Mode. I am using Tavily for case laws.")
            st.rerun()
    with col2:
        if st.button("🛒 Market Scout"):
            # UPDATED: Using Tavily for Market Research
            if 'auditor_report' in st.session_state:
                with st.spinner("🌐 Tavily Agent scouting the web..."):
                    # Search for real alternatives
                    tavily_data = tavily_search.tavily_deep_search("Best Health Insurance India 2025 comparison")
                    client = utils.initialize_gemini()
                    # Pass Tavily data to Gemini to summarize
                    res = client.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=f"Context from Web: {tavily_data}. User Policy: {st.session_state.auditor_report}. Compare and suggest switch."
                    )
                    add_message("assistant", res.text)
            else:
                st.toast("Upload a document first!")
            st.rerun()

# ... (Keep Main Content & Upload Logic) ...

# --- UPDATED AUDITOR LOGIC WITH CRITIC ---
if uploaded_file and client:
    if 'current_file_name' not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
        # ... (File processing & encoding logic same as before) ...
        
            # 1. Run Auditor
            report = auditor.generate_risk_assessment(client, "Scan this.", data, mime)
            
            if report:
                # 2. Run Critic (Reflexion Step)
                # We pass a snippet of text if possible, or just rely on Auditor's logic check
                final_report = critic.review_report(client, report, "Check for consistency.")
                
                st.session_state.auditor_report = final_report
                
                # Display
                doc_type = final_report.get('doc_type', 'Document')
                score = final_report.get('risk_score_0_to_100', 'N/A')
                
                # Check if Critic added a warning
                critic_note = ""
                if 'CRITIC_WARNING' in final_report:
                    critic_note = f"\n\n🕵️ **Critic's Note:** {final_report['CRITIC_WARNING']}"

                msg = f"""
                ✅ **{doc_type} Analyzed (Critically Reviewed)**
                
                **Score:** {score}/100
                
                🚩 **Risks:** {final_report.get('bad_clauses')}
                {critic_note}
                """
                add_message("assistant", msg)
                
                # ... (Family Check logic) ...
            
            st.rerun()

# --- UPDATED CHAT LOGIC WITH TAVILY ---
if prompt := st.chat_input("Ask..."):
    # ... (User message add logic) ...
    
    with st.chat_message("assistant"):
        # ... (Routing Logic) ...
        
        # Sentinel / Scam Check using TAVILY
        if any(x in prompt.lower() for x in ["scam", "fraud", "news"]):
            with st.spinner("🕵️ Sentinel using Tavily Search..."):
                search_data = tavily_search.tavily_deep_search(f"{prompt} insurance scam reviews")
                res = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=f"Web Evidence: {search_data}. User Query: {prompt}. Answer user."
                )
                st.markdown(res.text)
                add_message("assistant", res.text)
        
        # ... (Other logic same) ...
