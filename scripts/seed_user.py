# scripts/seed_user.py
import sqlite3, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent   # go up to repo root
DB   = ROOT / "app" / "finance_tracker.db"

email    = os.environ["FT_USER"]
password = os.environ["FT_PASS"]

with sqlite3.connect(DB) as conn:
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (email, password))
        conn.commit()
        print("User seeded")
    except sqlite3.IntegrityError:
        print("User already exists")