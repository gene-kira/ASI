# 🌟 MagicBox Swarm Defense Engine
import tkinter as tk
import random, math, threading, time, os, importlib
import hashlib, base64, json

# 🚀 Autoload Core Libraries
required_libs = ["tkinter", "math", "random", "threading", "time", "os", "importlib", "hashlib", "base64", "json"]
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        os.system(f"pip install {lib}")

# 🛡️ Data Lifespan Control Vault
class SensitiveDataVault:
    def __init__(self):
        self.personal_data = {}

    def store_data(self, key, value):
        self.personal_data[key] = {"value": value, "timestamp": time.time()}

    def purge_expired(self):
        now = time.time()
        for key in list(self.personal_data.keys()):
            if now - self.personal_data[key]['timestamp'] >= 86400:
                del self.personal_data[key]

    def simulate_backdoor_attempt(self, key):
        if key in self.personal_data:
            print(f"⚠️ Unauthorized data access: {key}")
            threading.Timer(3, lambda: self.self_destruct(key)).start()

    def self_destruct(self, key):
        print(f"💣 Data {key} has been erased.")
        if key in self.personal_data:
            del self.personal_data[key]

vault = SensitiveDataVault()

# 👁️ Trust Management System
class TrustEngine:
    def __init__(self):
        self.trusted_agents = set()

    def verify(self, identity):
        return identity in self.trusted_agents

    def register(self, identity):
        self.trusted_agents.add(identity)

trust_engine = TrustEngine()

# 🔥 Telemetry Pulse Generator
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

# 🔐 Glyph Cipher Encryption Layer
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

glyph_cipher = GlyphCipher("retina_swirl_v47")  # Customize seed

# 🌀 Unified Trust Node (visual + trust logic)
class TrustNode:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.node_id = f"agent_{random.randint(1000, 9999)}"
        self.trust_score = 100.0
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        trust_engine.register(self.node_id)

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

    def shift_trust(self, delta):
        prev = self.trust_score
        self.trust_score += delta
        if abs(prev - self.trust_score) >= 10:
            print(f"🔺 Trust shift for {self.node_id}: {prev} → {self.trust_score}")
            emit_glyph_packet()

# ⚡ Glyph Packet Emitter
def emit_glyph_packet():
    packet = telemetry_system.generate_packet()
    cipher = glyph_cipher.encrypt(packet)
    print(f"🔐 Glyph Packet Emitted: {cipher}")

# 🌌 Neural GUI Loop
def launch_network_gui():
    root = tk.Tk()
    root.title("🧠 Swarm Dream Engine - MagicBox")
    root.geometry("720x520")
    root.configure(bg="#0B0E1A")

    canvas_width = 700
    canvas_height = 460
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    node_count = 40
    nodes = [TrustNode(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()
            node.shift_trust(random.choice([-5, +5]))

        for i in range(node_count):
            for j in range(i + 1, node_count):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)

        vault.purge_expired()
        emit_glyph_packet()
        root.after(30, animate)

    animate()
    root.mainloop()

# 🚀 Launch It All
if __name__ == "__main__":
    launch_network_gui()

