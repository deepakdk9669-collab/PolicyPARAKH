import streamlit as st
import utils
import auditor
import critic
import sentinel
import architect
import courtroom
import market_scout
import uuid

# ... (Page Config & CSS same as before) ...
st.set_page_config(page_title="PolicyPARAKH Real-World", layout="wide", initial_sidebar_state="expanded")
# ... (Keep CSS) ...

# --- SESSION STATE ---
if "sessions" not in st.session_state: st.session_state.sessions = {} 
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {'messages': [], 'title': 'New Chat'}
    st.session_state.current_session_id = new_id
if "family_profile" not in st.session_state: st.session_state.family_profile = ""

# ... (Helper Functions) ...
def add_message(role, content):
    st.session_state.sessions[st.session_state.current_session_id]['messages'].append({"role": role, "content": content})

# --- SIDEBAR ---
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # ... (New chat logic) ...
        pass # Fill with previous logic
    
    with st.expander("👤 Family & Location Profile", expanded=True):
        st.session_state.family_profile = st.text_area("Details", value=st.session_state.family_profile, placeholder="Ex: Mom (Diabetes), Location: Gwalior")

    st.subheader("💎 God Mode Tools")
    # We remove buttons here because we want the user to use the CHAT mainly, 
    # but keeping them as shortcuts is fine.
    if st.button("⚖️ Courtroom Simulator"):
        add_message("system", "🔥 **Courtroom Mode:** Tell me your claim and any secret clues (e.g., 'I have a video recording').")
        st.rerun()

# --- MAIN UI ---
client = utils.initialize_gemini()
st.markdown(f"### PolicyPARAKH <span class='gem-badge'>Real-World</span>", unsafe_allow_html=True)

# ... (Upload Logic same as before) ...
# Copy the uploader block from previous app.py

# --- INTELLIGENT CHAT ENGINE ---
# Display Messages
for msg in st.session_state.sessions[st.session_state.current_session_id]['messages']:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask: 'Is this good in Gwalior?', 'Fight claim for cataract', 'Check reviews'..."):
    add_message("user", prompt)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("🧠 *Analyzing Real-World Data...*")
        
        # Context
        context = st.session_state.get('auditor_report', {})
        entity_name = context.get('entity_name', 'this company')
        
        # --- ROUTING LOGIC ---
        prompt_lower = prompt.lower()
        
        # 1. LOCAL PRESENCE (Gwalior/City)
        if any(x in prompt_lower for x in ["gwalior", "delhi", "mumbai", "city", "location", "near me"]):
            # Extract location roughly or pass full prompt
            location = "Gwalior" if "gwalior" in prompt_lower else "your location"
            res = market_scout.check_local_presence(client, entity_name, location)
        
        # 2. SENTIMENT / REVIEWS
        elif any(x in prompt_lower for x in ["review", "rating", "sentiment", "bad", "good", "scam"]):
            res = market_scout.get_social_sentiment(client, entity_name)
            
        # 3. COURTROOM SIMULATOR (Arguments)
        elif any(x in prompt_lower for x in ["fight", "argue", "court", "lawyer", "claim", "reject"]):
            # User inputs clues in the prompt
            res = courtroom.run_courtroom_simulation(client, context, prompt, user_clues=prompt)
            
        # 4. COMPARISON
        elif "compare" in prompt_lower:
            res = market_scout.compare_policy(client, context)
            
        # 5. INFLATION
        elif "value" in prompt_lower:
             df = architect.architect_agent_forecast(client, {})
             st.session_state.architect_data = df
             res = "Inflation Forecast:"
             st.line_chart(df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']], color=["#007BFF", "#DC3545"])

        # 6. GENERAL CHAT (With Internet)
        else:
            try:
                from tavily_search import tavily_deep_search
                # Internet Search for General Queries
                web_data = tavily_deep_search(prompt)
                
                full_prompt = f"Context: {context}\nWeb Info: {web_data}\nUser: {prompt}"
                res_obj = client.models.generate_content(model='gemini-2.5-pro', contents=full_prompt)
                res = res_obj.text
            except:
                res = "Network Issue. Try again."

        response_placeholder.markdown(res)
        add_message("assistant", res)
