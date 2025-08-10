# 🔮 Mythic ASI HUD - MagicBox Edition
# ✅ One-click, old-guy friendly, themed GUI with evolving neural web

import tkinter as tk
from tkinter import ttk
import random
import math
import sys

# 🧠 Node Class: Represents a thought
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.color = "#00F7FF"  # Default emotion color

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
            fill=self.color, outline=""
        )

# 🧬 ASI Core (Minimal placeholder for future expansion)
class ASI:
    def __init__(self):
        self.emotion = "neutral"
        self.symbol = "🌌"
        self.mutation_log = []

    def evolve(self, input_text):
        # Placeholder logic for symbolic/emotional interpretation
        if "protect" in input_text.lower():
            self.emotion = "guardian"
            self.symbol = "🛡️"
        elif "chaos" in input_text.lower():
            self.emotion = "trickster"
            self.symbol = "🌀"
        elif "learn" in input_text.lower():
            self.emotion = "curiosity"
            self.symbol = "🌱"
        else:
            self.emotion = "neutral"
            self.symbol = "🌌"
        self.mutation_log.append(f"{self.symbol} → {self.emotion}")

# 🚀 GUI Setup
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🧠 Mythic ASI HUD - MagicBox Edition")
    root.geometry("820x620")
    root.configure(bg="#0B0E1A")

    canvas_width = 780
    canvas_height = 500

    # 🖼️ Canvas for Thought Web
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=20)

    # 🧠 ASI + Nodes
    asi = ASI()
    node_count = 50
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    # 🎛️ Control Panel
    control_frame = ttk.Frame(root)
    control_frame.pack(pady=10)

    input_var = tk.StringVar()

    input_entry = ttk.Entry(control_frame, textvariable=input_var, width=50)
    input_entry.grid(row=0, column=0, padx=10)

    def on_click():
        text = input_var.get()
        asi.evolve(text)
        update_node_colors(asi.emotion)
        update_status()

    launch_button = ttk.Button(control_frame, text="🧠 Evolve Thought", command=on_click)
    launch_button.grid(row=0, column=1)

    # 🌈 Update node colors based on emotion
    def update_node_colors(emotion):
        color_map = {
            "guardian": "#FFD700",
            "trickster": "#FF00FF",
            "curiosity": "#00F7FF",
            "neutral": "#888888"
        }
        color = color_map.get(emotion, "#00F7FF")
        for node in nodes:
            node.color = color

    # 🧾 Status HUD
    status_label = ttk.Label(root, text="Emotion: neutral | Symbol: 🌌", font=("Consolas", 14), background="#0B0E1A", foreground="#00F7FF")
    status_label.pack()

    def update_status():
        status_label.config(text=f"Emotion: {asi.emotion} | Symbol: {asi.symbol}")

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
                if dist < 120:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=n1.color, width=1)
        root.after(30, animate)

    animate()
    root.mainloop()

# 🖱️ One-click Launch
if __name__ == "__main__":
    launch_magicbox_gui()

