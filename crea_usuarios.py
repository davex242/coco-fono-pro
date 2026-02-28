# crea_usuarios.py

import sqlite3
from datetime import datetime

conn = sqlite3.connect("coco_fono.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role, is_active, created_at)
VALUES (?, ?, ?, ?, ?)
""", ("admin", "admin123", "admin", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

cursor.execute("""
INSERT OR IGNORE INTO users (username, password, role, is_active, created_at)
VALUES (?, ?, ?, ?, ?)
""", ("user", "user123", "user", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

conn.commit()
conn.close()

print("✔ Usuarios creados en texto plano.")
