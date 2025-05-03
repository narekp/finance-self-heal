# scripts/seed_user.py
import sqlite3, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent   # go up to repo root
DB   = ROOT / "app" / "finance_tracker.db"

username = os.environ["FT_USER"]
password = os.environ["FT_PASS"]
# for four-column table
email    = os.environ.get("FT_EMAIL", f"example@example.com")
phone    = os.environ.get("FT_PHONE", "37444444444")

with sqlite3.connect(DB) as conn:
    c = conn.cursor()
    
    # make sure we have a users table (this DOES NOT redefine an existing one)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    # Now inspect its columns
    cols = [row[1] for row in c.execute("PRAGMA table_info(users)")]

    try:
        if set(["username","email","phone","password"]).issubset(cols):
            # four-column schema
            c.execute(
                "INSERT OR IGNORE INTO users(username,email,phone,password) VALUES(?,?,?,?)",
                (username, email, phone, password)
            )
        else:
            # two-column schema
            c.execute(
                "INSERT OR IGNORE INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
        conn.commit()
        print("User seeded")
    except sqlite3.Error as e:
        print("Seeding error:", e)