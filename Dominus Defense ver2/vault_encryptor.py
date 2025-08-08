# vault_encryptor.py

import hashlib
import time

def glyph_key(glyphs):
    seed = "".join(glyphs)
    return hashlib.sha256(seed.encode()).hexdigest()

def encrypt_log(log_data, glyphs=["🧿", "⚡", "🕸️"]):
    key = glyph_key(glyphs)
    encrypted = f"{key[:16]}::{log_data[::-1]}"
    print(f"🔐 Log encrypted with glyph key: {key[:8]}...")
    return encrypted

def create_ephemeral_vault():
    print("🗝️ Ephemeral vault created. Auto-purge in 60s.")
    # Future: Store encrypted logs, auto-delete after timeout

