import sqlite3
import pandas as pd

conn = sqlite3.connect("user_logs.db")
df = pd.read_sql_query("SELECT * FROM logs", conn)
print(df)
conn.close()
