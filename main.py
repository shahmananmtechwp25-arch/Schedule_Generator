import streamlit as st
from openai import OpenAI

# This pulls the key from the TOML secrets you just pasted
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("API Key not found in Streamlit Secrets!")
# Configuration
st.set_page_config(page_title="ImpactLog AI", layout="wide")
db_conn = init_db()

# Security: Pulling the API Key from Streamlit Secrets (Global)
# Or from Sidebar for Local testing
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not api_key:
    api_key = st.secrets.get("OPENAI_API_KEY", "")

st.title("🚀 Worklog to Performance Quantifier")
st.info("M.Tech Project: Agentic Workflow for Career Achievement Transformation")

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Daily Logs")
    user_input = st.text_area("What did you achieve today?", height=200, 
                             placeholder="e.g., optimized the sql queries and met the client")
    
    if st.button("💾 Save & Transform"):
        if user_input and api_key:
            # 1. Save locally (Persistence)
            save_log(db_conn, user_input)
            
            # 2. Transform via AI (Logic)
            client = OpenAI(api_key=api_key)
            with st.spinner("Analyzing impact..."):
                prompt = f"""
                Transform these notes into professional achievements using the STAR method:
                NOTES: {user_input}
                
                Format as:
                - Weekly Summary
                - Professional Self-Appraisal (STAR Method)
                - LinkedIn 'Friday Win' Post
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.session_state['result'] = response.choices[0].message.content
        else:
            st.error("Missing Input or API Key!")

with col2:
    st.subheader("✨ Professional Output")
    if 'result' in st.session_state:
        st.markdown(st.session_state['result'])
        st.download_button("Export Report", st.session_state['result'], file_name="Achievement_Report.md")

# Research Data Section
st.divider()
st.subheader("📊 Data Persistence History (Offline/Local Storage)")
history = get_history(db_conn)
st.dataframe(history, use_container_width=True)
