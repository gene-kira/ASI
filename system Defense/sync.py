from cryptography.fernet import Fernet
import json

sync_key = Fernet.generate_key()
cipher = Fernet(sync_key)

def encrypt_payload(payload):
    return cipher.encrypt(json.dumps(payload).encode())

def decrypt_payload(payload):
    return json.loads(cipher.decrypt(payload).decode())

