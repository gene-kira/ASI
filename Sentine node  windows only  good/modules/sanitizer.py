# sanitizer.py — Ruthless Data Hygiene
import time

class DataSanitizer:
    def __init__(self):
        self.expiry_registry = []

    def tag_backdoor_data(self, payload):
        self.expiry_registry.append((time.time() + 3, payload))
        return "[SANITIZER] Backdoor data tagged for purge in 3 sec."

    def tag_mac_ip(self, identifier):
        self.expiry_registry.append((time.time() + 30, identifier))
        return "[SANITIZER] MAC/IP tagged for purge in 30 sec."

    def tag_personal_data(self, data):
        self.expiry_registry.append((time.time() + 86400, data))
        return "[SANITIZER] Personal data tagged for purge in 1 day."

    def tag_fake_telemetry(self, telemetry):
        self.expiry_registry.append((time.time() + 30, telemetry))
        return "[SANITIZER] Fake telemetry tagged for purge in 30 sec."

    def purge_expired(self):
        now = time.time()
        self.expiry_registry = [(t, d) for t, d in self.expiry_registry if t > now]

