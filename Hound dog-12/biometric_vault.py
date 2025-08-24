import time
import json
from cryptography.fernet import Fernet

vault_key = Fernet.generate_key()
vault = Fernet(vault_key)
biometric_store = []

def store_biometric(data, source):
    expiry = time.time() + 86400
    encrypted = vault.encrypt(json.dumps(data).encode())
    biometric_store.append({"data": encrypted, "source": source, "expires": expiry})
    print(f"[Biometric Vault] Stored biometric from {source}")

def purge_expired_biometrics(mutation_output=None):
    now = time.time()
    before = len(biometric_store)
    biometric_store[:] = [b for b in biometric_store if b["expires"] > now]
    purged = before - len(biometric_store)
    if purged > 0 and mutation_output:
        mutation_output.insert("end", f"💣 Purged {purged} expired biometric entries\n")
    if purged > 0:
        print(f"[Biometric Vault] Purged {purged} expired entries")

