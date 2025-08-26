# overlay.py
import tkinter as tk
import random

class NeuralOverlay:
    def __init__(self, root, memory):
        self.canvas = tk.Canvas(root, width=700, height=300, bg="black")
        self.canvas.pack()
        self.draw_nodes(memory)

    def draw_nodes(self, memory):
        for item in memory:
            x, y = random.randint(50, 650), random.randint(50, 250)
            color = "#%02x%02x%02x" % (
                item['weight'] * 2 % 255,
                item['novelty'] * 2 % 255,
                150
            )
            self.canvas.create_oval(x, y, x+10, y+10, fill=color)
            label = item.get('process') or f"Port {item.get('port')}" or item.get('type', 'Node')
            self.canvas.create_text(x+15, y, text=label, fill="white", anchor="w")

            if item.get("type") == "fusion":
                self.canvas.create_oval(x-2, y-2, x+12, y+12, outline="cyan")

