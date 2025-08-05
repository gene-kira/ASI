import time
import hashlib
import threading
from datetime import datetime, timedelta

# --- Data Classification ---
class DataPacket:
    def __init__(self, data, data_type, origin, timestamp=None):
        self.data = data
        self.data_type = data_type  # 'personal', 'system', 'unknown'
        self.origin = origin  # e.g. 'internal', 'external', 'backdoor'
        self.timestamp = timestamp or datetime.now()
        self.hash_id = hashlib.sha256(data.encode()).hexdigest()

# --- Security Engine ---
class OvermindSecuritySystem:
    def __init__(self):
        self.registry = {}
        self.zero_trust_active = True

    def register_packet(self, packet: DataPacket):
        self.registry[packet.hash_id] = packet
        self.evaluate_packet(packet)

    def evaluate_packet(self, packet: DataPacket):
        # Backdoor auto-self destruct (3 sec)
        if packet.origin == 'backdoor':
            threading.Timer(3.0, self.self_destruct, args=[packet.hash_id]).start()

        # Personal data auto-destruction in 1 day
        elif packet.data_type == 'personal':
            delay = timedelta(days=1).total_seconds()
            threading.Timer(delay, self.self_destruct, args=[packet.hash_id]).start()

        # Zero-trust scanner
        if self.zero_trust_active:
            self.zero_trust_check(packet)

    def self_destruct(self, hash_id):
        if hash_id in self.registry:
            del self.registry[hash_id]
            print(f"[Self-Destruct] DataPacket {hash_id} purged.")

    def zero_trust_check(self, packet: DataPacket):
        if packet.origin != 'internal':
            print(f"[Zero Trust] Unverified origin: {packet.origin}. Locking access.")
            # Lock or escalate logic here

# --- Sample Insertion ---
if __name__ == "__main__":
    sec_sys = OvermindSecuritySystem()

    test_backdoor = DataPacket("Sensitive Info A", "system", "backdoor")
    test_personal = DataPacket("User Profile X", "personal", "external")

    sec_sys.register_packet(test_backdoor)
    sec_sys.register_packet(test_personal)

