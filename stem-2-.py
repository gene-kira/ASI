import subprocess
import sys
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox

# 🔧 Autoloader: Ensures all mythic modules are summoned
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

# 🧠 Node Class for Neural Web
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

# 🚀 GUI Setup: Neural Web Interface
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

    # 🕸️ Initialize nodes
    node_count = 40
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    # 🔁 Animation Loop
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

# 🎨 MagicBox GUI Core
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

    root.mainloop()

# 🧠 Launch Both Interfaces
launch_magicbox_gui()
launch_network_gui()

