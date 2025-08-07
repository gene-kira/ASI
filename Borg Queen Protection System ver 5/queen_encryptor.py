# queen_encryptor.py
import os, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Encryptor:
    def __init__(self):
        self.key_vault = {}  # key_id: (key, expiry)
        self.audit_log = []

    def generate_key(self, key_id, ttl=30):
        key = AESGCM.generate_key(bit_length=256)
        expiry = time.time() + ttl
        self.key_vault[key_id] = (key, expiry)
        self.audit_log.append(f"glyph(keygen:{key_id})")
        return key

    def purge_expired_keys(self):
        now = time.time()
        self.key_vault = {k: (v, exp) for k, (v, exp) in self.key_vault.items() if exp > now}

    def encrypt_file(self, filepath, key_id):
        self.purge_expired_keys()
        if key_id not in self.key_vault:
            raise Exception("Key expired or missing")
        key, _ = self.key_vault[key_id]
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        with open(filepath, "rb") as f:
            data = f.read()
        encrypted = aesgcm.encrypt(nonce, data, None)

        with open(filepath + ".enc", "wb") as f:
            f.write(nonce + encrypted)

        self.audit_log.append(f"glyph(encrypt:{filepath})")

    def decrypt_file(self, enc_path, key_id, output_path):
        self.purge_expired_keys()
        if key_id not in self.key_vault:
            raise Exception("Key expired or missing")
        key, _ = self.key_vault[key_id]
        aesgcm = AESGCM(key)

        with open(enc_path, "rb") as f:
            raw = f.read()
        nonce = raw[:12]
        encrypted = raw[12:]
        decrypted = aesgcm.decrypt(nonce, encrypted, None)

        with open(output_path, "wb") as f:
            f.write(decrypted)

        self.audit_log.append(f"glyph(decrypt:{output_path})")

    def get_audit_log(self):
        return self.audit_log[-5:]

