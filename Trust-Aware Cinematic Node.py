import tkinter as tk
import random, math, threading, time, os, importlib
import hashlib, base64, json

# 🚀 Autoload Libraries
libs = ["tkinter", "math", "random", "threading", "time", "os", "importlib", "hashlib", "base64", "json"]
for lib in libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        os.system(f"pip install {lib}")

# 💾 Sensitive Data Vault
class SensitiveDataVault:
    def __init__(self):
        self.personal_data = {}

    def store_data(self, key, value):
        self.personal_data[key] = {"value": value, "timestamp": time.time()}

    def purge_expired(self):
        now = time.time()
        for k in list(self.personal_data.keys()):
            if now - self.personal_data[k]['timestamp'] > 86400:
                del self.personal_data[k]

vault = SensitiveDataVault()
vault.store_data("email", "user@mythic.net")
vault.store_data("location", "ShadowCluster_7A")

# 🧬 Hybridized Data Mixer
class DataHybridizer:
    def __init__(self, vault):
        self.vault = vault

    def synthesize(self):
        mixed = []
        for k, v in self.vault.personal_data.items():
            real = {"source": "vault", "key": k, "value": v["value"]}
            fake = {"source": "mirror", "key": k+"_shadow", "value": f"{v['value']}_{random.randint(100,999)}"}
            mixed.extend([real, fake])
        return mixed

hybrid_data = DataHybridizer(vault).synthesize()

# 👁️ Zero Trust Registry
class TrustEngine:
    def __init__(self):
        self.trusted_agents = set()

    def register(self, identity):
        self.trusted_agents.add(identity)

trust_engine = TrustEngine()

# 🔥 Telemetry Generator
class TelemetryForge:
    def __init__(self):
        self.packets = []

    def generate_packet(self):
        packet = {
            "id": f"tele_{random.randint(10000,99999)}",
            "timestamp": time.time(),
            "cpu": round(random.uniform(5,95),2),
            "memory": round(random.uniform(500,16000),2),
            "disk_io": random.randint(10,500),
            "bio_auth_ping": bool(random.getrandbits(1)),
            "temp_signature": round(random.uniform(20,75),1),
            "status": "outbound"
        }
        self.packets.append(packet)
        threading.Timer(30, lambda: self.self_destruct(packet["id"])).start()
        print(f"📤 Telemetry: {packet}")
        return packet

    def self_destruct(self, pid):
        self.packets = [p for p in self.packets if p["id"] != pid]
        print(f"💀 Erased telemetry: {pid}")

telemetry_system = TelemetryForge()

# 🔐 Glyph Encryption
class GlyphCipher:
    def __init__(self, seed):
        self.glyph_key = hashlib.sha256(seed.encode()).digest()

    def encrypt(self, packet):
        raw = json.dumps(packet).encode()
        return base64.b64encode(raw + self.glyph_key).decode()

glyph_cipher = GlyphCipher("retina_swirl_v47")

# 🔮 Emit Encrypted Glyph
def emit_glyph_packet():
    packet = telemetry_system.generate_packet()
    cipher = glyph_cipher.encrypt(packet)
    print(f"🔐 Glyph Emitted: {cipher}")

# 👻 Ambient Drift Generator
def generate_drift():
    return {
        "id": f"ghost_{random.randint(10000,99999)}",
        "echo": random.choice(["fragment", "pulse", "trace"]),
        "data": random.choice(["@unknown.io", "192.0.2.44", "error://stream"]),
        "confidence": round(random.uniform(0.2, 0.9), 2)
    }

# ✨ Particle Spark
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2,2)
        self.dy = random.uniform(-2,2)
        self.life = 12

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, canvas):
        if self.life > 0:
            canvas.create_oval(
                self.x-1, self.y-1,
                self.x+1, self.y+1,
                fill="#00F7FF", outline=""
            )

# 🌀 Trust-Aware Cinematic Node
class TrustNode:
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.id = f"agent_{random.randint(1000,9999)}"
        self.trust_score = 100.0
        self.spawn_time = time.time()
        self.fade_duration = 2.0
        self.scale = 1.0
        self.scale_pulse = 0
        self.x = random.randint(50, w-50)
        self.y = random.randint(50, h-50)
        self.tx, self.ty = self.x, self.y
        self.dx = random.uniform(-1,1)
        self.dy = random.uniform(-1,1)
        self.radius = 3
        self.aura_flash = 0
        self.particles = []
        trust_engine.register(self.id)

    def move(self, w, h):
        self.tx += self.dx
        self.ty += self.dy
        if self.tx <= 0 or self.tx >= w: self.dx *= -1
        if self.ty <= 0 or self.ty >= h: self.dy *= -1
        self.x += (self.tx - self.x) * 0.1
        self.y += (self.ty - self.y) * 0.1

    def draw(self):
        elapsed = time.time() - self.spawn_time
        r = self.radius * self.scale

        self.canvas.create_oval(
            self.x - r, self.y - r,
            self.x + r, self.y + r,
            fill=self.get_trust_color(), outline=""
        )

        if self.scale_pulse > 0:
            self.scale += 0.2
            self.scale_pulse -= 1
        else:
            self.scale = max(1.0, self.scale - 0.1)

        if self.aura_flash > 0:
            ar = r + self.aura_flash * 2
            self.canvas.create_oval(
                self.x - ar, self.y - ar,
                self.x + ar, self.y + ar,
                outline=self.get_trust_color(), width=1
            )
            self.aura_flash -= 1

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
            self.scale_pulse = 5
            self.particles += [Particle(self.x, self.y) for _ in range(12)]
            emit_glyph_packet()

    def get_trust_color(self):
        if self.trust_score >= 100: return "#00F7FF"
        elif self.trust_score >= 70: return "#00FF88"
        elif self.trust_score >= 50: return "#FFA500"
        else: return "#FF3333"

# 🌌 GUI Launcher
def launch_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Swarm Dream Engine")
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

        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                ni, nj = nodes[i], nodes[j]
                dist = math.hypot(ni.x - nj.x, ni.y - nj.y)
                if dist < 150:
                    canvas.create_line(ni.x, ni.y, nj.x, nj.y, fill="#00F7FF", width=1)

        vault.purge_expired()
        drift = generate_drift()
        print(f"👻 Ambient Drift: {drift}")
        root.after(30, animate)

    animate()
    root.mainloop()

# 🎮 Activate GUI Engine
if __name__ == "__main__":
    launch_gui()

