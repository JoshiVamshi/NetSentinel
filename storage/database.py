# storage/database.py

import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        src_ip TEXT,
        src_port INTEGER,
        dst_ip TEXT,
        dst_port INTEGER,
        protocol TEXT,
        attack_type TEXT,
        severity TEXT,
        packet_count INTEGER,
        byte_count INTEGER,
        duration REAL,
        reason TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_alert(flow, detection):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO alerts VALUES (
        NULL,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """, (
        datetime.utcnow().isoformat(),
        flow.src_ip,
        flow.src_port,
        flow.dst_ip,
        flow.dst_port,
        flow.protocol,
        detection["attack_type"],
        detection["severity"],
        flow.packet_count,
        flow.byte_count,
        flow.duration(),
        detection["reason"]
    ))

    conn.commit()
    conn.close()
