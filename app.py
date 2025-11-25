import streamlit as st
import utils
import auditor
import sentinel
import architect

# Page Config
st.set_page_config(page_title="PolicyPARAKH Pro", layout="wide")

# Custom CSS
st.markdown("""
<style>
.stApp { font-family: 'Inter', sans-serif; }
h1 { color: #007BFF; text-align: center; }
.risk-meter { border: 3px solid #007BFF; border-radius: 0.75rem; padding: 1.5rem; text-align: center; background-color: #e9ecef; }
.risk-score { font-size: 4rem; font-weight: 900; }
.tech-badge { background-color: #e3f2fd; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; color: #0d47a1; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("PolicyPARAKH: Neural Legal Defense System")
    st.markdown("<center><span class='tech-badge'>Powered by Gemini 3 Pro Preview & Gemini 2.5 Flash</span></center>", unsafe_allow_html=True)
    st.markdown("##### The AI that reads the fine print and fights for you.")
    
    # 1. Initialize
    client = utils.initialize_gemini()
    if not client: return

    # 2. Sidebar Input
    st.sidebar.header("Input Policy")
    uploaded_file = st.sidebar.file_uploader("Upload Policy (PDF)", type="pdf")

    if uploaded_file and 'pdf_base64' not in st.session_state:
        st.session_state.pdf_base64 = utils.base64_encode_pdf(uploaded_file)
        st.sidebar.success("✅ Policy ingested.")
        if 'auditor_report' in st.session_state: del st.session_state.auditor_report
        if 'architect_data' in st.session_state: del st.session_state.architect_data

    # 3. Agent Controls
    if st.sidebar.button("Run Auditor Scan (Gemini 3 Pro)") and uploaded_file:
        prompt = "Analyze for Room Rent, Co-Pay, and Exclusions."
        report = auditor.generate_risk_assessment(client, prompt, st.session_state.pdf_base64)
        if report:
            st.session_state.auditor_report = report

    if 'auditor_report' in st.session_state:
        if st.sidebar.button("Run Architect Forecast (Live Data)"):
            st.session_state.architect_data = architect.architect_agent_forecast(client, st.session_state.auditor_report)

    # 4. Dashboard Display
    st.markdown("---")
    
    # Auditor Section
    if 'auditor_report' in st.session_state and st.session_state.auditor_report:
        report = st.session_state.auditor_report
        st.header("Auditor Risk Assessment")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            score = report['risk_score_0_to_100']
            color = 'red' if score > 70 else ('orange' if score > 40 else 'green')
            st.markdown(f"<div class='risk-meter' style='border-color:{color};'><p>Risk Score</p><p class='risk-score' style='color:{color}'>{score}</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Insurer:** {report.get('insurance_company_name', 'Unknown')}")
            st.markdown(f"**Co-Pay:** {report['co_pay_clause']}")
            st.markdown(f"**Room Rent:** {report['room_rent_limit']}")
            st.info(f"**Summary:** {report['auditor_summary']}")
        st.markdown("---")

    # Architect Section
    if 'architect_data' in st.session_state:
        df = st.session_state.architect_data
        rate_used = df.attrs.get('inflation_rate_used', 10)
        
        st.subheader("Architect Agent: Future Value Forecast")
        st.warning(f"📉 **Real-Time Data Used:** Calculated using the current **{rate_used}% Medical Inflation Rate** found online.")
        
        st.line_chart(
            df.set_index('Year')[['Actual_Coverage_Value', 'Real_Purchasing_Power']],
            color=["#007BFF", "#DC3545"]
        )
        st.markdown("---")

    # 5. Chat Interface
    st.subheader("Unified Chatbot (Ask about Scams, Value, or Law)")
    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about your policy..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            if 'pdf_base64' not in st.session_state:
                st.write("Please upload a PDF first.")
            else:
                prompt_lower = prompt.lower()
                
                # Sentinel (Gemini 2.5) for Search
                if any(k in prompt_lower for k in ["scam", "fraud", "review", "complaint", "settlement", "ratio"]):
                    response = sentinel.sentinel_agent_check(client, st.session_state.auditor_report, prompt)
                
                # Architect for Finance
                elif any(k in prompt_lower for k in ["value", "worth", "inflation", "future"]):
                    if 'architect_data' in st.session_state:
                         response = "See the inflation chart above."
                    else:
                        response = "Click 'Run Architect Forecast' to see financial data."
                
                # Chat fallback (Gemini 3 Pro) for reasoning
                else:
                    # Using Gemini 3 Pro for normal chat reasoning too
                    context = f"Policy Summary: {st.session_state.get('auditor_report')}. User: {prompt}"
                    res = client.models.generate_content(model='gemini-3-pro-preview', contents=context)
                    response = res.text
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
