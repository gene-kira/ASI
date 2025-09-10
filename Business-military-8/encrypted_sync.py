# encrypted_sync.py

import json
import hashlib
from cryptography.fernet import Fernet

class EncryptedSync:
    def __init__(self, node_id, secret_key):
        self.node_id = node_id
        self.fernet = Fernet(secret_key)

    def encrypt_codex(self, codex):
        payload = json.dumps({
            "node": self.node_id,
            "codex": codex
        }).encode("utf-8")
        return self.fernet.encrypt(payload)

    def decrypt_codex(self, encrypted_payload):
        try:
            decrypted = self.fernet.decrypt(encrypted_payload)
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            return None

    def verify_integrity(self, codex):
        return hashlib.sha256(json.dumps(codex).encode()).hexdigest()

