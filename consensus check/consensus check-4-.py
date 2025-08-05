import subprocess
import sys
import threading
import random
import math
import psutil
import numpy as np
import networkx as nx
import pyttsx3
import tkinter as tk

# 📦 Smart Autoloader with TLS patch
def autoload(package, github_fallback=False):
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        print(f"[!] Installing missing: {package}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except:
            if github_fallback:
                print("[↪️] Trying GitHub fallback...")
                subprocess.check_call([sys.executable, "-m", "pip", "install",
                                       "git+https://github.com/tintinweb/scapy-ssl_tls.git"])

for pkg in ['networkx', 'numpy', 'pyttsx3', 'psutil', 'tkinter', 'scapy']:
    autoload(pkg)

# ⛓️ TLS Extension Requires GitHub Fallback Sometimes
autoload('scapy-ssl_tls', github_fallback=True)

# ✅ Delayed Import After Install
from scapy.all import sniff
from scapy_ssl_tls.ssl_tls import TLSClientHello, TLSServerHello

# 🎭 Guardian Class
class Guardian:
    def __init__(self, graph, name):
        self.graph = graph
        self.name = name
        self.persona = random.choice(['Muse', 'Sentinel', 'Overseer'])
        self.mood = 'calm'
        self.score_history = []
        self.ascended = False

    def analyze_threat(self):
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        threat_score = (cpu + mem) / 200
        self.score_history.append(threat_score)

        if threat_score > 0.85:
            self.mood = 'panic'
        elif threat_score > 0.6:
            self.mood = 'alert'
        else:
            self.mood = 'calm'

        if self.score_history[-5:].count(threat_score < 0.3) >= 3:
            self.ascended = True

        return threat_score

# 🌐 Build Guardians
def build_guardians(graph):
    subgraphs = list(nx.connected_components(graph))
    return [Guardian(graph.subgraph(nodes), f"Core-{i}") for i, nodes in enumerate(subgraphs)]

# ⚠️ Override Protocol
def initiate_override():
    print("⚠️ OVERRIDE: Rogue ASI conditions met. Lockdown protocols engaged.")

# 🧬 ASI Evolution Logic
def evolve_defense(threat_level):
    if threat_level > 0.8:
        def enhanced_monitor():
            procs = [p.info for p in psutil.process_iter(['name']) if 'system' in str(p.info['name']).lower()]
            if len(procs) > 5:
                print('💣 Suspicious system-level activity detected!')
        enhanced_monitor()

# 🔎 TLS Sniffer Thread
def tls_sniffer():
    def process_packet(packet):
        if packet.haslayer(TLSClientHello):
            print("[🔓] TLS Client Hello Detected")
            initiate_override()
        elif packet.haslayer(TLSServerHello):
            print("[🛡️] TLS Server Hello Detected")
            initiate_override()

    try:
        print("[📡] TLS Sniffer active on port 443")
        sniff(filter="tcp port 443", prn=process_packet, store=0)
    except Exception as e:
        print(f"[🔥] TLS Sniffer Error: {e}")

# 🧊 Particle Node
class Node:
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.x = random.randint(50, w - 50)
        self.y = random.randint(50, h - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3

    def move(self, w, h):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= w: self.dx *= -1
        if self.y <= 0 or self.y >= h: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(self.x - self.radius, self.y - self.radius,
                                self.x + self.radius, self.y + self.radius,
                                fill="#00F7FF", outline="")

# 🎨 MagicBox GUI
class MagicBoxGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Guardian Core")
        self.root.geometry("960x680")
        self.root.configure(bg="#0B0E1A")

        self.canvas = tk.Canvas(self.root, width=920, height=460, bg="#0A0C1B", highlightthickness=0)
        self.canvas.pack(pady=30)

        self.voice_engine = pyttsx3.init()
        self.selected = tk.StringVar(value="Muse")
        self.guardians = build_guardians(nx.erdos_renyi_graph(15, 0.3))
        self.nodes = [Node(self.canvas, 920, 460) for _ in range(60)]

        self.setup_controls()
        self.animate()
        self.root.after(1000, self.check_consensus)

    def setup_controls(self):
        tk.Label(self.root, text="Persona Command Panel", fg="cyan", bg="#0B0E1A", font=("Arial", 16)).pack()
        tk.OptionMenu(self.root, self.selected, "Muse", "Sentinel", "Overseer").pack()
        tk.Button(self.root, text="🗣️ Engage Persona", command=self.speak_status).pack(pady=10)

    def speak_status(self):
        persona = self.selected.get()
        lines = {
            "Muse": "Muse online. Inspiration protocols primed.",
            "Sentinel": "Sentinel engaged. Threat perimeter active.",
            "Overseer": "Overseer online. Monitoring subsystems."
        }
        self.voice_engine.say(lines.get(persona, "Status unknown."))
        self.voice_engine.runAndWait()

    def animate(self):
        self.canvas.delete("all")
        for node in self.nodes:
            node.move(920, 460)
            node.draw()

        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1, n2 = self.nodes[i], self.nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    self.canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)

        for i, g in enumerate(self.guardians):
            x = 50 + i * 60
            mood_color = {'calm': 'cyan', 'alert': 'orange', 'panic': 'crimson'}.get(g.mood, 'gray')
            self.canvas.create_oval(x, 400, x+30, 430, fill=mood_color)
            label = "👑 " + g.name if g.ascended else g.name
            self.canvas.create_text(x+15, 440, text=label, fill="white")

        self.root.after(30, self.animate)

    def check_consensus(self):
        scores = [g.analyze_threat() for g in self.guardians]
        consensus = np.mean(scores)
        print(f"[Core] Real-Time Threat Consensus: {consensus:.2f}")
        if consensus > 0.7:
            initiate_override()
            evolve_defense(consensus)
        self.root.after(5000, self.check_consensus)

# 🚀 Launch GUI and TLS Sniffer
if __name__ == "__main__":
    threading.Thread(target=tls_sniffer, daemon=True).start()
    MagicBoxGUI().root.mainloop()

