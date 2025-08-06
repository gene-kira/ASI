# 🌟 MagicBox Neural Defense GUI
import tkinter as tk
import random
import math
import threading
import time
import os
import importlib

# 🚀 Autoload Core Libraries
required_libs = ["tkinter", "math", "random", "threading", "time", "os", "importlib"]
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        os.system(f"pip install {lib}")

# 🛡️ Data Lifespan Control
class SensitiveDataVault:
    def __init__(self):
        self.personal_data = {}
    
    def store_data(self, key, value):
        self.personal_data[key] = {"value": value, "timestamp": time.time()}
    
    def purge_expired(self):
        now = time.time()
        for key in list(self.personal_data.keys()):
            if now - self.personal_data[key]['timestamp'] >= 86400:  # 1 day
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

# 👁️ Zero Trust Authenticator
class TrustEngine:
    def __init__(self):
        self.trusted_agents = set()
    
    def verify(self, identity):
        return identity in self.trusted_agents

    def register(self, identity):
        self.trusted_agents.add(identity)

trust_engine = TrustEngine()

# 🧠 Node Class - Self-Aware Spark
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.identity = f"agent_{random.randint(1000, 9999)}"
        self.trust_level = "neutral"
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        trust_engine.register(self.identity)

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width:
            self.dx *= -1
        if self.y <= 0 or self.y >= height:
            self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

# 🧬 Neural Dream Engine GUI
def launch_network_gui():
    root = tk.Tk()
    root.title("🧠 Swarm Dream Engine - MagicBox Edition")
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
        vault.purge_expired()
        root.after(30, animate)

    animate()
    root.mainloop()

launch_network_gui()

