import subprocess
import sys
import os
import json
import time
import math
import random
import threading
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

# 🔧 Autoloader
def autoload_libraries():
    required = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'pywin32': 'pywin32',
        'opencv-python': 'opencv-python',
        'pygame': 'pygame',
        'tkinterdnd2': 'tkinterdnd2'
    }
    for lib, pip_name in required.items():
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

autoload_libraries()

# 🧠 Codex Rewrite Logic
CODEX_FILE = "fusion_codex.json"

class Pulse:
    def __init__(self, port, entropy):
        self.port = port
        self.entropy = entropy

def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote(pulse):
    votes = [random.choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = random.randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🌐 Real-Time Port Scanner
def scan_live_flows():
    flows = []
    conns = psutil.net_connections(kind='inet')
    for conn in conns:
        try:
            laddr = conn.laddr.port
            raddr = conn.raddr.port if conn.raddr else 0
            status = conn.status
            proto = "TCP" if conn.type == psutil.SOCK_STREAM else "UDP"
            entropy = (
                abs(laddr - raddr) / 100 +
                (1 if status not in ["ESTABLISHED", "LISTEN"] else 0) +
                (1.5 if proto == "UDP" else 1)
            )
            flows.append(Pulse(port=laddr, entropy=entropy))
        except Exception:
            continue
    return flows

# 🔁 Mutation Monitor
def monitor_ports_and_mutate(gui_callback=None):
    flows = []
    while True:
        new_flows = scan_live_flows()
        flows.extend(new_flows)
        flows = flows[-50:]
        if detect_density_spike(flows):
            pulse = new_flows[-1]
            if initiate_mutation_vote(pulse):
                entry = rewrite_optimization_logic()
                store_rewrite_codex(entry)
                print("[🜂 Mutation] Codex updated.")
                if gui_callback:
                    gui_callback()
        time.sleep(3)

# 🎨 MagicBox GUI
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🜁 MagicBox Daemon 🜄")
    root.geometry("900x600")
    root.configure(bg="#0b0b0b")
    root.resizable(False, False)

    header = tk.Label(root, text="🜁 MagicBox Daemon 🜄", font=("Orbitron", 28, "bold"), fg="#00ffe0", bg="#0b0b0b")
    header.pack(pady=20)

    status_frame = tk.Frame(root, bg="#1a1a1a", bd=2, relief="groove")
    status_frame.pack(pady=10, padx=30, fill="x")

    status_label = tk.Label(status_frame, text="Status: Swarm Sync Active", font=("Consolas", 14), fg="#00ff88", bg="#1a1a1a")
    status_label.pack(pady=10)

    def ingest_signal():
        status_label.config(text="🜁 Ingesting Signal...")
        root.after(1500, lambda: status_label.config(text="🜂 Mutation Complete"))

    ingest_btn = ttk.Button(root, text="🜁 Ingest Signal", command=ingest_signal)
    ingest_btn.pack(pady=20)

    sigil_frame = tk.Frame(root, bg="#0b0b0b")
    sigil_frame.pack(pady=10)

    sigil_chain = tk.Label(sigil_frame, text="🜁 → 🜂 → 🜄", font=("Consolas", 20), fg="#ff00aa", bg="#0b0b0b")
    sigil_chain.pack()

    def show_codex_hint():
        messagebox.showinfo("Codex Vault", "🜁 = Ingest\n🜂 = Mutate\n🜄 = Defend\n🜅 = Overlay")

    codex_btn = ttk.Button(root, text="🧠 View Codex Hint", command=show_codex_hint)
    codex_btn.pack(pady=10)

    footer = tk.Label(root, text="Codex Vault Secure • Zero Trust Spine Engaged", font=("Consolas", 10), fg="#888", bg="#0b0b0b")
    footer.pack(side="bottom", pady=10)

    def gui_mutation_feedback():
        status_label.config(text="🜂 Mutation Triggered")
        sigil_chain.config(text="🜁 → 🜂 → 🜄 → 🜆")

    threading.Thread(target=monitor_ports_and_mutate, args=(gui_mutation_feedback,), daemon=True).start()
    root.mainloop()

# 🕸️ Neural Web Interface
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.dy = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.radius = 4

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > width:
            self.dx *= -1
        if self.y < 0 or self.y > height:
            self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

def launch_network_gui():
    root = tk.Tk()
    root.title("🧠 Neural Web Interface")
    root.geometry("720x520")
    root.configure(bg="#0B0E1A")

    canvas_width = 700
    canvas_height = 460
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    node_count = 40
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()
        for i in range(node_count):
            for j in range(i + 1, node_count):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)
        root.after(30, animate)

    animate()
    root.mainloop()

# 🚀 Launch Daemon Interfaces
threading.Thread(target=launch_network_gui, daemon=True).start()
launch_magicbox_gui()

