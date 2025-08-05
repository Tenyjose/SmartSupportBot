# init_db.py
import sqlite3

conn = sqlite3.connect("user_logs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    intent TEXT,
    user_message TEXT,
    department TEXT,
    date TEXT,
    time TEXT,
    doctor TEXT,
    symptom TEXT
)
""")

conn.commit()
conn.close()

print("✅ SQLite database and table created successfully.")
