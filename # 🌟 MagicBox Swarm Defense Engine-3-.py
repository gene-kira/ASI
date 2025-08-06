import tkinter as tk
import random, math, threading, time, os, importlib
import hashlib, base64, json

# 🚀 Core Library Check
required_libs = ["tkinter", "math", "random", "threading", "time", "os", "importlib", "hashlib", "base64", "json"]
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        os.system(f"pip install {lib}")

# 🛡️ Vault
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

vault = SensitiveDataVault()

# 👁️ Trust Registry
class TrustEngine:
    def __init__(self):
        self.trusted_agents = set()

    def register(self, identity):
        self.trusted_agents.add(identity)

trust_engine = TrustEngine()

# 🔥 Telemetry Forge
class TelemetryForge:
    def __init__(self):
        self.packets = []

    def generate_packet(self):
        packet = {
            "id": f"tele_{random.randint(10000,99999)}",
            "timestamp": time.time(),
            "cpu": round(random.uniform(5, 95), 2),
            "memory": round(random.uniform(500, 16000), 2),
            "disk_io": random.randint(10, 500),
            "bio_auth_ping": bool(random.getrandbits(1)),
            "temp_signature": round(random.uniform(20, 75), 1),
            "status": "outbound"
        }
        self.packets.append(packet)
        threading.Timer(30, lambda: self.self_destruct(packet["id"])).start()
        print(f"📤 Telemetry: {packet}")
        return packet

    def self_destruct(self, packet_id):
        self.packets = [p for p in self.packets if p["id"] != packet_id]
        print(f"💀 Erased: {packet_id}")

telemetry_system = TelemetryForge()

# 🔐 Glyph Cipher
class GlyphCipher:
    def __init__(self, seed):
        self.glyph_key = hashlib.sha256(seed.encode()).digest()

    def encrypt(self, packet):
        raw = json.dumps(packet).encode()
        cipher = base64.b64encode(raw + self.glyph_key)
        return cipher.decode()

glyph_cipher = GlyphCipher("retina_swirl_v47")

# 🌟 Particle Spark
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = 12

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, canvas):
        if self.life > 0:
            canvas.create_oval(
                self.x - 1, self.y - 1,
                self.x + 1, self.y + 1,
                fill="#00F7FF", outline=""
            )

# 🌀 Trust Node w/ Aura + Particles
class TrustNode:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.id = f"agent_{random.randint(1000,9999)}"
        self.trust_score = 100.0
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.aura_flash = 0
        self.particles = []
        trust_engine.register(self.id)

    def move(self, w, h):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= w: self.dx *= -1
        if self.y <= 0 or self.y >= h: self.dy *= -1

    def draw(self):
        # Base node
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )
        # Aura
        if self.aura_flash > 0:
            r = self.radius + self.aura_flash * 2
            color = self.get_trust_color()
            self.canvas.create_oval(
                self.x - r, self.y - r,
                self.x + r, self.y + r,
                outline=color, width=1
            )
            self.aura_flash -= 1

        # Particle burst
        for p in self.particles[:]:
            p.move()
            p.draw(self.canvas)
            if p.life <= 0:
                self.particles.remove(p)

    def shift_trust(self, delta):
        prev = self.trust_score
        self.trust_score += delta
        if abs(prev - self.trust_score) >= 10:
            print(f"🔺 {self.id}: {prev} → {self.trust_score}")
            self.aura_flash = 15
            self.particles += [Particle(self.x, self.y) for _ in range(10)]
            emit_glyph_packet()

    def get_trust_color(self):
        if self.trust_score >= 100: return "#00F7FF"  # Electric blue
        elif self.trust_score >= 70: return "#00FF88"  # Green
        elif self.trust_score >= 50: return "#FFA500"  # Orange
        else: return "#FF3333"       # Red

# 🔐 Emit Glyph
def emit_glyph_packet():
    packet = telemetry_system.generate_packet()
    cipher = glyph_cipher.encrypt(packet)
    print(f"🔐 Glyph Emitted: {cipher}")

# 🌌 GUI Overmind
def launch_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Swarm Engine")
    root.geometry("720x520")
    root.configure(bg="#0B0E1A")

    cw, ch = 700, 460
    canvas = tk.Canvas(root, width=cw, height=ch, bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [TrustNode(canvas, cw, ch) for _ in range(40)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(cw, ch)
            node.draw()
            node.shift_trust(random.choice([-5, +5]))

        # Draw links
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                ni, nj = nodes[i], nodes[j]
                dist = math.hypot(ni.x - nj.x, ni.y - nj.y)
                if dist < 150:
                    canvas.create_line(ni.x, ni.y, nj.x, nj.y, fill="#00F7FF", width=1)

        vault.purge_expired()
        root.after(30, animate)

    animate()
    root.mainloop()

# 🎮 Run Engine
if __name__ == "__main__":
    launch_gui()

