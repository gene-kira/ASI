import os, json
from cryptography.fernet import Fernet
from config import MEMORY_FILE, VAULT_KEY_FILE

def get_vault_key():
    if not os.path.exists(VAULT_KEY_FILE):
        key = Fernet.generate_key()
        with open(VAULT_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(VAULT_KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

vault = get_vault_key()

def log_threat_to_memory(threat):
    data = json.dumps(threat).encode()
    encrypted = vault.encrypt(data)
    with open(MEMORY_FILE, "ab") as f:
        f.write(encrypted + b"\n")

