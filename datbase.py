import sqlite3
import pandas as pd

def init_db():
    """Initializes the local database for offline persistence."""
    conn = sqlite3.connect("worklogs.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def save_log(conn, text):
    """Saves a raw worklog entry locally."""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (raw_text) VALUES (?)", (text,))
    conn.commit()

def get_history(conn):
    """Retrieves all historical logs for analysis."""
    return pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)
