import random, time, threading, hashlib, base64, json

# 🔥 Ephemeral Fake Telemetry Generator
class TelemetryForge:
    def __init__(self):
        self.packets = []

    def generate_packet(self):
        packet = {
            "id": f"tele_{random.randint(10000,99999)}",
            "timestamp": time.time(),
            "cpu": round(random.uniform(5.0, 98.3), 2),
            "memory": round(random.uniform(100.0, 16000.0), 2),
            "disk_io": random.randint(10, 500),
            "bio_auth_ping": bool(random.getrandbits(1)),
            "temp_signature": round(random.uniform(20.0, 75.0), 1),
            "status": "outbound"
        }
        self.packets.append(packet)
        threading.Timer(30, lambda: self.self_destruct(packet["id"])).start()
        print(f"📤 Sent Telemetry: {packet}")
        return packet

    def self_destruct(self, packet_id):
        self.packets = [p for p in self.packets if p["id"] != packet_id]
        print(f"💀 Telemetry {packet_id} auto-erased after 30s.")

telemetry_system = TelemetryForge()

# 🔐 Glyph Encryption Engine
class GlyphCipher:
    def __init__(self, biometric_seed):
        self.glyph_key = hashlib.sha256(biometric_seed.encode()).digest()

    def encrypt(self, packet):
        raw = json.dumps(packet).encode()
        cipher = base64.b64encode(raw + self.glyph_key)
        return cipher.decode()

    def decrypt(self, cipher_text):
        try:
            raw = base64.b64decode(cipher_text.encode())
            payload = raw[:-len(self.glyph_key)]
            return json.loads(payload)
        except Exception:
            return None

glyph_cipher = GlyphCipher("retina_swirl_v47")  # Customize seed as needed

# 🌀 Trust-Responsive Node Framework
class TrustNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.trust_score = 100.0  # Mutable trust meter

    def shift_trust(self, delta):
        prev_score = self.trust_score
        self.trust_score += delta
        if abs(prev_score - self.trust_score) >= 10:
            print(f"🔺 Trust shift detected for {self.node_id}: {prev_score} → {self.trust_score}")
            emit_glyph_packet()

def emit_glyph_packet():
    packet = telemetry_system.generate_packet()
    cipher = glyph_cipher.encrypt(packet)
    print(f"🔐 Glyph Packet Emitted: {cipher}")

# ⚙️ Fusion Hook (example use in animate loop or agent tick)
def agent_tick():
    for _ in range(2):
        telemetry_system.generate_packet()
    # Simulate trust shift
    demo_node = TrustNode("agent_007")
    demo_node.shift_trust(random.choice([-12, +15]))

# 🌌 Run Simulation
if __name__ == "__main__":
    while True:
        agent_tick()
        time.sleep(5)  # Control pulse rate

