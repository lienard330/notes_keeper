# encryption.py
from cryptography.fernet import Fernet
import os

KEY_FILE = "encryption.key"

def load_key():
    """Load or generate encryption key."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# Load the key when module is imported
key = load_key()
cipher = Fernet(key)

def encrypt_text(text: str) -> str:
    """Encrypt plain text into a secure string."""
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    """Decrypt encrypted string back into plain text."""
    return cipher.decrypt(encrypted_text.encode()).decode()
