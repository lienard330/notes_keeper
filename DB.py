import sqlite3
import bcrypt
import re
from encryption import encrypt_text, decrypt_text

DB_NAME = "notes.db"

# ==================== INIT DB ====================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            is_premium INTEGER DEFAULT 0
        )
    """)

    # Notes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# ==================== PASSWORD VALIDATION ====================

def is_strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must include at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must include at least one special character (!@#$ etc.)"
    return True, "Strong password."

# ==================== USER FUNCTIONS ====================

def create_user(username, password):
    """Register a new user with hashed password."""
    valid, msg = is_strong_password(password)
    if not valid:
        return False, f"❌ Weak password: {msg}"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True, "✅ User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "⚠ Username already exists!"
    finally:
        conn.close()

def check_login(username, password):
    """Verify login. Returns (user_id, is_premium) if valid, else None."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, password_hash, is_premium FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode("utf-8"), row[1]):
        return row[0], row[2]
    return None

def register_user(username, password):
    return create_user(username, password)

def login_user(username, password):
    return check_login(username, password)

# ==================== NOTES FUNCTIONS ====================

def upgrade_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_premium=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def add_note(user_id, title, content):
    encrypted_content = encrypt_text(content)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
              (user_id, title, encrypted_content))
    conn.commit()
    conn.close()

def get_notes(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM notes WHERE user_id=?", (user_id,))
    notes = c.fetchall()
    conn.close()
    # Decrypt notes
    decrypted_notes = []
    for n in notes:
        try:
            decrypted_notes.append((n[0], n[1], decrypt_text(n[2])))
        except Exception:
            decrypted_notes.append((n[0], n[1], "[Decryption Error]"))
    return decrypted_notes

def update_note(note_id, title, content):
    encrypted_content = encrypt_text(content)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, encrypted_content, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

# ==================== AUTO INIT ====================
init_db()
