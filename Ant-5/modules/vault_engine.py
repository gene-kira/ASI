from cryptography.fernet import Fernet
import time

class VaultEngine:
    def __init__(self, ttl=60):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.store = {}
        self.ttl = ttl

    def save(self, label, data):
        encrypted = self.cipher.encrypt(data.encode())
        self.store[label] = (encrypted, time.time())

    def retrieve(self, label):
        if label in self.store:
            encrypted, timestamp = self.store[label]
            if time.time() - timestamp < self.ttl:
                return self.cipher.decrypt(encrypted).decode()
            else:
                del self.store[label]
        return None

    def purge(self):
        now = time.time()
        for label in list(self.store.keys()):
            _, timestamp = self.store[label]
            if now - timestamp >= self.ttl:
                del self.store[label]

