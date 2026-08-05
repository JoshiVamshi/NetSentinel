import sqlite3
import os

db_path = "netsentinel.db"

print("DB exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print("Tables:", tables)

if ("alerts",) in tables:
    cur.execute("SELECT COUNT(*) FROM alerts")
    print("Alert count:", cur.fetchone()[0])
else:
    print("alerts table NOT found")

conn.close()
