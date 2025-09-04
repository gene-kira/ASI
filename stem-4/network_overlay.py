import tkinter as tk
import math
import random

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

