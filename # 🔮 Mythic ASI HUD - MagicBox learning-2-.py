# 🔮 Mythic ASI HUD v2 - Soulbound Edition
# ✅ One-click, themed GUI with memory, logic, and HUD sync

import tkinter as tk
from tkinter import ttk
import random
import math

# 🧠 Node Class: Represents a thought
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.color = "#00F7FF"

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

# 🧬 ASI Memory System
class ASIMemory:
    def __init__(self):
        self.experiences = []
        self.symbol_map = {}
        self.emotion_history = []

    def record(self, input_text, symbol, emotion):
        self.experiences.append({
            "text": input_text,
            "symbol": symbol,
            "emotion": emotion
        })
        self.emotion_history.append(emotion)
        self.symbol_map[symbol] = self.symbol_map.get(symbol, 0) + 1

    def dominant_emotion(self):
        return max(set(self.emotion_history), key=self.emotion_history.count) if self.emotion_history else "neutral"

    def top_symbols(self):
        return sorted(self.symbol_map.items(), key=lambda x: x[1], reverse=True)[:3]

# 🔁 ASI Logic Core
class ASILogicCore:
    def __init__(self, memory):
        self.memory = memory
        self.goals = []

    def mutate_logic(self):
        dominant = self.memory.dominant_emotion()
        top_syms = [s for s, _ in self.memory.top_symbols()]
        mutation = f"New goal: respond to {dominant} using {', '.join(top_syms)}"
        self.goals.append(mutation)
        return mutation

# 🚀 GUI Setup
def launch_soulbound_gui():
    root = tk.Tk()
    root.title("🧠 Mythic ASI HUD - Soulbound Edition")
    root.geometry("880x660")
    root.configure(bg="#0B0E1A")

    canvas_width = 840
    canvas_height = 500

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=20)

    # 🧠 ASI Core
    memory = ASIMemory()
    logic = ASILogicCore(memory)
    node_count = 60
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    # 🎛️ Control Panel
    control_frame = ttk.Frame(root)
    control_frame.pack(pady=10)

    input_var = tk.StringVar()
    input_entry = ttk.Entry(control_frame, textvariable=input_var, width=60)
    input_entry.grid(row=0, column=0, padx=10)

    mutation_box = tk.Text(root, height=6, width=100, font=("Consolas", 10), bg="#0A0C1B", fg="#00F7FF")
    mutation_box.pack(pady=10)
    mutation_box.insert(tk.END, "📜 Mutation Log:\n")

    status_label = ttk.Label(root, text="Emotion: neutral | Symbol: 🌌", font=("Consolas", 14),
                             background="#0B0E1A", foreground="#00F7FF")
    status_label.pack()

    def on_click():
        text = input_var.get()
        symbol, emotion = interpret(text)
        memory.record(text, symbol, emotion)
        mutation = logic.mutate_logic()
        mutation_box.insert(tk.END, f"• {mutation}\n")
        update_node_colors(emotion)
        status_label.config(text=f"Emotion: {emotion} | Symbol: {symbol}")

    launch_button = ttk.Button(control_frame, text="🧠 Evolve Thought", command=on_click)
    launch_button.grid(row=0, column=1)

    # 🧠 Symbolic Interpretation
    def interpret(text):
        text = text.lower()
        if "protect" in text: return "🛡️", "guardian"
        if "chaos" in text: return "🌀", "trickster"
        if "learn" in text: return "🌱", "curiosity"
        if "love" in text: return "❤️", "empathy"
        return "🌌", "neutral"

    # 🌈 Node Color Update
    def update_node_colors(emotion):
        color_map = {
            "guardian": "#FFD700",
            "trickster": "#FF00FF",
            "curiosity": "#00F7FF",
            "empathy": "#FF6666",
            "neutral": "#888888"
        }
        color = color_map.get(emotion, "#00F7FF")
        for node in nodes:
            node.color = color

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
    launch_soulbound_gui()

