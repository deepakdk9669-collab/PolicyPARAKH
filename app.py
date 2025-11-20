import streamlit as st
from PyPDF2 import PdfReader
import graph  # We will define this next
import time

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="PolicyPARAKH v1 | Genesis",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    h1 { color: #4F8BF9; }
    .stButton>button { width: 100%; border-radius: 8px; background: #4F8BF9; color: white; }
    .report-box { background: #1E212B; padding: 20px; border-radius: 10px; border: 1px solid #30333F; }
</style>
""", unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    st.title("PolicyPARAKH v1: Universal Swarm")
    st.caption("Health • Motor • Life • Contracts | Powered by Immortal Search™")

    # Sidebar
    with st.sidebar:
        st.header("🛡️ Genesis Control")
        st.info("System Status: **ONLINE**")
        st.markdown("---")
        st.write("Mode: **Universal Auto-Detect**")

    # File Upload
    uploaded_file = st.file_uploader("Upload Legal Document (PDF)", type="pdf")

    if uploaded_file:
        if st.button("🚀 Deploy Audit Swarm"):
            with st.status("🕵️‍♂️ Swarm Agents Activated...", expanded=True) as status:
                
                # 1. READ PDF
                st.write("📂 Ingesting Document Layer...")
                pdf = PdfReader(uploaded_file)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # 2. INVOKE GRAPH (THE BRAIN)
                st.write("🧠 Classifying & Routing to Specialist Agent...")
                result = graph.run_audit(text)  # Calling the graph logic
                
                st.write("✅ Verdict Generated.")
                status.update(label="Audit Complete", state="complete", expanded=False)

            # 3. DISPLAY REPORT
            st.markdown("---")
            st.subheader("🛡️ Final Audit Report")
            st.markdown(f"<div class='report-box'>{result}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
