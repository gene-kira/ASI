import tkinter as tk
import random
import math
from datetime import datetime

# 🧠 System Memory
SYSTEM_MEMORY = {
    "telemetry": [],
    "purges": [],
    "threats": [],
    "events": []
}

# 🌐 Node Class with Reactive Behavior
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.status = "normal"
        self.status_timer = 0

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1
        if self.status != "normal":
            self.status_timer -= 1
            if self.status_timer <= 0:
                self.status = "normal"

    def draw(self):
        color = {
            "normal": "#00F7FF",
            "telemetry": "#00FFFF",
            "purge": "#FF4444",
            "threat": "#FFFF00"
        }.get(self.status, "#00F7FF")

        size = self.radius if self.status == "normal" else self.radius + 2
        self.canvas.create_oval(
            self.x - size, self.y - size,
            self.x + size, self.y + size,
            fill=color, outline=""
        )

# 🔮 Trace Event Function
def trace_event(category, details):
    timestamp = datetime.now().isoformat()
    trace = f"{category}:{timestamp}:{details}"
    SYSTEM_MEMORY[category].append(trace)
    SYSTEM_MEMORY["events"].append(trace)
    print(f"[🔮] Trace: {trace}")

    # Trigger node reactions
    if category in ["telemetry", "purges", "threats"]:
        for node in nodes:
            node.status = category if category != "purges" else "purge"
            node.status_timer = 10

# 🎨 Animation Loop
def animate():
    canvas.delete("all")
    for node in nodes:
        node.move(WIDTH, HEIGHT)
        node.draw()

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1, n2 = nodes[i], nodes[j]
            dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
            if dist < 150:
                if n1.status == "purge" or n2.status == "purge":
                    color = "#FF4444"
                elif n1.status == "telemetry" or n2.status == "telemetry":
                    color = "#00FFFF"
                elif n1.status == "threat" or n2.status == "threat":
                    color = "#FFFF00"
                else:
                    color = "#00F7FF"
                canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=color, width=1)

    root.after(50, animate)

# 🧭 Event Buttons
def send_telemetry():
    trace_event("telemetry", "Dispatching encrypted telemetry burst")

def purge_data():
    trace_event("purges", "Initiating data purge protocol")

def block_threat():
    trace_event("threats", "Threat neutralized and cloaked")

# 🖼️ GUI Setup
WIDTH, HEIGHT = 800, 600
root = tk.Tk()
root.title("Mythic Swarm Interface")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# 🧬 Node Initialization
nodes = [Node(canvas, WIDTH, HEIGHT) for _ in range(50)]

# 🧪 Control Panel
control_frame = tk.Frame(root, bg="black")
control_frame.pack(pady=10)

tk.Button(control_frame, text="📡 Send Telemetry", command=send_telemetry, bg="#00FFFF", fg="black").pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="🧹 Purge Data", command=purge_data, bg="#FF4444", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="🛡️ Block Threat", command=block_threat, bg="#FFFF00", fg="black").pack(side=tk.LEFT, padx=5)

# 🚀 Launch Animation
animate()
root.mainloop()

