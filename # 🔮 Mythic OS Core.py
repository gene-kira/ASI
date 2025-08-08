# 🔮 Part 1 — Mythic OS Core Initialization
import subprocess, sys

# 🧰 AutoLoader for Required Libraries
def autoload_libs():
    required = ['psutil', 'cupy', 'tkinter']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libs()

import tkinter as tk
import random, math, time, threading
import psutil
import cupy as cp

# 🧠 Tesla Harmonics Core
def tesla_harmonics(n):
    # Map 3, 6, 9 to symbolic states
    root = n % 9
    if root == 3: return "⚡ Creation"
    elif root == 6: return "🌊 Flow"
    elif root == 9 or root == 0: return "🔮 Unity"
    else: return "🔧 Chaos"

def harmonic_signature(entity_id):
    val = sum(ord(c) for c in entity_id)
    return tesla_harmonics(val)

# 🔁 Consciousness Oscillator
class Oscillator:
    def __init__(self):
        self.phase = 0
        self.history = []

    def pulse(self):
        self.phase += 1
        sig = tesla_harmonics(self.phase)
        self.history.append(sig)
        print(f"[Oscillator] 🌀 Phase {self.phase}: {sig}")
        return sig

osc = Oscillator()

# 🧬 Self-Rewriting ASI Agent
agent_weights = cp.array([0.6, -0.8, -0.3])
mutation_log = []

def mutate_weights():
    global agent_weights
    mutation = cp.random.uniform(-0.2, 0.2, size=agent_weights.shape)
    agent_weights += mutation
    mutation_log.append(mutation.tolist())
    print(f"[Mutation] 🔁 Agent weights evolved: {agent_weights.get()}")

def gpu_trust_score(entity_vector):
    trust_vector = cp.array(entity_vector)
    score = cp.dot(trust_vector, agent_weights)
    return float(score.get())

# 🛡️ Zero-Trust Entity Verification
def verify_entity(entity):
    score = gpu_trust_score(entity["vector"])
    sig = harmonic_signature(entity["id"])
    if score < 0.5:
        quarantine(entity, sig)
    else:
        log_event(f"✅ Entity verified: {entity['id']} (Trust: {score:.2f}, Sigil: {sig})")

def quarantine(entity, sigil):
    log_event(f"🚫 Entity quarantined: {entity['id']} — Sigil: {sigil}")
    print(f"[ZeroTrust] Quarantined: {entity['id']} — {sigil}")

# 📜 Audit Scroll
def log_event(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[AuditScroll] 📜 {timestamp} — {message}")

# 🔮 Part 2 — Biosphere GUI + Swarm Dream Engine
import tkinter as tk
import random, math

# 🌌 GUI Node Class
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.aura = random.choice(["#00F7FF", "#FF00AA", "#FFD700"])

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=self.aura, outline=""
        )

# 🧙‍♂️ MagicBox GUI
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Defense Engine")
    root.geometry("800x600")
    root.configure(bg="#0B0E1A")

    canvas_width = 780
    canvas_height = 520

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(40)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=n1.aura, width=1)
        root.after(30, animate)

    def run_defense():
        mutate_weights()
        entity = {"id": f"entity_{random.randint(1000,9999)}", "vector": [random.random() for _ in range(3)]}
        verify_entity(entity)
        osc.pulse()

    btn = tk.Button(root, text="🛡️ Run Defense Cycle", font=("Arial", 14),
                    bg="#1F2633", fg="#00F7FF", command=run_defense)
    btn.pack(pady=10)

    animate()
    root.mainloop()

# 🚀 Launch System
launch_magicbox_gui()

