# ─────────────────────────────────────────────────────────────
# 🔧 Autoloader
import subprocess, sys
def autoload(pkgs):
    for pkg in pkgs:
        try: __import__(pkg)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
autoload(["torch", "tkinter"])

# ─────────────────────────────────────────────────────────────
# 📜 Imports
import threading, queue, time, random, signal, socket, torch
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 📜 Forensic Logging
LOG_FILE = "mutation_trace.log"
def log_event(msg, cat):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [{cat}] {msg}\n")

# ─────────────────────────────────────────────────────────────
# 🧠 S-bit Data Packet
class DataPacket:
    def __init__(self, payload, priority, origin, lineage):
        self.payload = payload
        self.priority = priority
        self.origin = origin
        self.lineage = lineage
        self.timestamp = time.time()

    def __lt__(self, other):  # Fix for PriorityQueue comparison
        return self.timestamp < other.timestamp

# ─────────────────────────────────────────────────────────────
# 🛣️ Detour Engine
class DetourEngine:
    def __init__(self):
        self.stack = queue.PriorityQueue()
        self.detour_log = []
        self.codex = {"threshold": 10, "persona_shift": True}

    def ingest(self, packet):
        self.stack.put((packet.priority, packet))
        log_event(f"Ingested {packet.payload}", "INGRESS")

    def reroute(self):
        if self.stack.qsize() > self.codex["threshold"]:
            rerouted = []
            while not self.stack.empty():
                _, packet = self.stack.get()
                rerouted.append(packet)
            log_event(f"Detour triggered for {len(rerouted)} packets", "DETOUR")
            self.detour_log.append(f"Detour at {time.time()} for {len(rerouted)} packets")
            return rerouted
        return []

# ─────────────────────────────────────────────────────────────
# 🎭 Persona Glyph
class PersonaGlyph:
    def __init__(self, name, symbol, color, animation):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.animation = animation
        self.frame = 0

    def next_frame(self):
        self.frame = (self.frame + 1) % len(self.animation)
        return self.animation[self.frame]

# ─────────────────────────────────────────────────────────────
# 🧬 Borg Node
class BorgNode:
    def __init__(self, node_id, persona):
        self.node_id = node_id
        self.memory = []
        self.persona = persona
        self.glyph_state = "🟢"

    def sync(self, packet):
        self.memory.append(packet)
        if packet.priority > 7 and self.persona.name != "Shield":
            self.persona = PersonaGlyph("Shield", "🛡️", "red", ["🛡️", "🔰", "🛡️"])
        self.glyph_state = "🟡" if packet.priority > 5 else "🟢"
        log_event(f"Borg {self.node_id} synced {packet.payload}", "BORG")

# ─────────────────────────────────────────────────────────────
# ⚡ Hybrid Executor
class HybridExecutor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def process(self, packet):
        tensor = torch.tensor([ord(c) for c in packet.payload], dtype=torch.float32).to(self.device)
        mutated = torch.relu(tensor)
        log_event(f"Processed {packet.payload} on {self.device}", "PROCESS")
        return mutated.cpu().numpy()

# ─────────────────────────────────────────────────────────────
# 🛡️ DNS Suppression + Swarm Firewall
BLOCKED_DOMAINS = ["ads.example.com", "telemetry.tracker.net"]
class SwarmFirewall:
    def __init__(self, blocked):
        self.blocked = set(blocked)
        self.nodes = []

    def register(self, node): self.nodes.append(node)

    def enforce(self, domain):
        if domain in self.blocked:
            for node in self.nodes:
                node.glyph_state = "🔴"
                node.memory.append(f"Blocked {domain}")
            log_event(f"Swarm blocked {domain}", "FIREWALL")
            return "BLOCKED"
        return "ALLOWED"

def suppress_dns(domain):
    firewall = SwarmFirewall(BLOCKED_DOMAINS)
    return "0.0.0.0" if firewall.enforce(domain) == "BLOCKED" else socket.gethostbyname(domain)

# ─────────────────────────────────────────────────────────────
# 🧠 Daemon Core
class DaemonCore:
    def __init__(self): self.running = True
    def shutdown(self, *_): self.running = False; log_event("Daemon shutdown", "SYSTEM")
    def run(self, engine, borg_nodes, executor):
        while self.running:
            if engine.stack.qsize() > 0:
                _, packet = engine.stack.get()
                executor.process(packet)
                for node in borg_nodes: node.sync(packet)
            time.sleep(0.1)

# ─────────────────────────────────────────────────────────────
# 🎨 Glyph GUI Dashboard (50% smaller, auto-injecting)
class GlyphDashboard:
    def __init__(self, engine, borg_nodes):
        self.engine = engine
        self.borg_nodes = borg_nodes
        self.root = tk.Tk()
        self.root.title("ASI-Borg Sovereign Shell")
        self.canvas = tk.Canvas(self.root, width=400, height=200, bg="black")
        self.canvas.pack()
        self.status = ttk.Label(self.root, text="Daemon Active", font=("Consolas", 10))
        self.status.pack()
        self.inject_loop()
        self.update_loop()

    def draw_glyph(self, x, y, persona, glyph_state):
        symbol = persona.next_frame()
        color = persona.color if glyph_state != "🔴" else "red"
        self.canvas.create_text(x, y, text=symbol, fill=color, font=("Consolas", 12))

    def inject_loop(self):
        for i in range(5):
            packet = DataPacket(f"auto_{random.randint(1000,9999)}", random.randint(1, 10), "AutoIngress", f"mutation_{i}")
            self.engine.ingest(packet)
        rerouted = self.engine.reroute()
        self.status.config(text=f"Detour: {len(rerouted)} packets")
        self.root.after(3000, self.inject_loop)

    def update_loop(self):
        self.canvas.delete("all")
        for i, node in enumerate(self.borg_nodes):
            self.draw_glyph(50 + i * 100, 100, node.persona, node.glyph_state)
        self.root.after(500, self.update_loop)

    def run(self): self.root.mainloop()

# ─────────────────────────────────────────────────────────────
# 🚀 Launch System
if __name__ == "__main__":
    engine = DetourEngine()
    personas = [
        PersonaGlyph("Watcher", "👁️", "cyan", ["👁️", "👀", "👁️"]),
        PersonaGlyph("Seeker", "🔍", "yellow", ["🔍", "🧠", "🔍"]),
        PersonaGlyph("Shield", "🛡️", "orange", ["🛡️", "🔰", "🛡️"])
    ]
    borg_nodes = [BorgNode(i, personas[i]) for i in range(3)]
    firewall = SwarmFirewall(BLOCKED_DOMAINS)
    for node in borg_nodes: firewall.register(node)
    executor = HybridExecutor()
    daemon = DaemonCore()

    signal.signal(signal.SIGINT, daemon.shutdown)
    signal.signal(signal.SIGTERM, daemon.shutdown)

    threading.Thread(target=daemon.run, args=(engine, borg_nodes, executor), daemon=True).start()
    gui = GlyphDashboard(engine, borg_nodes)
    gui.run()
