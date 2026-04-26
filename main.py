import streamlit as st
from openai import OpenAI
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE LOGIC (Persistence Layer) ---
def init_db():
    conn = sqlite3.connect("worklog_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_input TEXT,
            transformed_output TEXT,
            timestamp DATETIME
        )
    """)
    conn.commit()
    return conn

def save_to_db(conn, raw, transformed):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (raw_input, transformed_output, timestamp) VALUES (?, ?, ?)",
        (raw, transformed, datetime.now())
    )
    conn.commit()

# --- 2. AI LOGIC (Processing Layer) ---
def transform_worklog(client, text):
    try:
        prompt = f"""
        Act as a professional career coach. Transform the following messy work notes 
        into a structured achievement report using the STAR method (Situation, Task, Action, Result).
        
        NOTES: {text}
        
        FORMAT:
        ### 🚀 Professional Summary
        [Write a high-level summary here]
        
        ### 📊 Key Achievements (STAR)
        [List points here]
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional technical writer."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Transformation Error: {str(e)}"

# --- 3. UI SETUP (Presentation Layer) ---
st.set_page_config(page_title="ImpactLog AI", page_icon="📝", layout="wide")

# Initialize Database
db_conn = init_db()

# Sidebar - API Configuration & History
with st.sidebar:
    st.title("⚙️ Settings")
    # Priority: 1. TOML Secrets (Cloud) | 2. User Input (Local Test)
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter OpenAI API Key:", type="password")
    
    st.divider()
    st.subheader("📜 Recent History")
    history_df = pd.read_sql_query("SELECT timestamp, raw_input FROM logs ORDER BY id DESC LIMIT 5", db_conn)
    st.table(history_df)

# Main Interface
st.title("👨‍💻 M.Tech Project: Global Worklog Generator")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Step 1: Input Daily Activity")
    raw_text = st.text_area("What did you work on today?", height=250, 
                            placeholder="e.g., fixed the css bug and had a sync meeting with the dev team")
    
    generate_btn = st.button("Generate & Save Report", use_container_width=True)

with col2:
    st.subheader("📤 Step 2: Professional Output")
    
    if generate_btn:
        if not api_key:
            st.error("Please provide an API Key in the sidebar or secrets.toml")
        elif not raw_text.strip():
            st.warning("Please enter some work notes first.")
        else:
            with st.spinner("AI is analyzing your impact..."):
                # Initialize Client
                client = OpenAI(api_key=api_key)
                
                # Process
                output = transform_worklog(client, raw_text)
                
                # Save to Local SQLite
                save_to_db(db_conn, raw_text, output)
                
                # Display
                st.markdown(output)
                st.download_button("Download Report (.md)", output, file_name=f"Worklog_{datetime.now().strftime('%Y%m%d')}.md")
    else:
        st.info("Your professionally formatted report will appear here.")

# Footer
st.divider()
st.caption("Built for M.Tech Final Project Submission | Powered by GPT-4o-mini & Streamlit Cloud")
