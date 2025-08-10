import tkinter as tk
from tkinter import ttk
import random
import math
import time

# 🧠 Node Class: Thought Web
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

# 💠 Goal Crystal Class
class GoalCrystal:
    def __init__(self, text, symbol, emotion, birth_time):
        self.text = text
        self.symbol = symbol
        self.emotion = emotion
        self.birth_time = birth_time
        self.size = 6
        self.orbit_radius = random.randint(100, 180)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = self.get_color(emotion)
        self.cluster_offset = random.uniform(-30, 30)

    def get_color(self, emotion):
        return {
            "guardian": "#FFD700",
            "trickster": "#FF00FF",
            "curiosity": "#00F7FF",
            "empathy": "#FF6666",
            "neutral": "#888888"
        }.get(emotion, "#00F7FF")

    def update(self):
        self.angle += 0.01
        self.size = min(12, self.size + 0.05)

    def draw(self, canvas, center_x, center_y):
        self.update()
        x = center_x + math.cos(self.angle) * (self.orbit_radius + self.cluster_offset)
        y = center_y + math.sin(self.angle) * (self.orbit_radius + self.cluster_offset)
        canvas.create_oval(
            x - self.size, y - self.size,
            x + self.size, y + self.size,
            fill=self.color, outline=""
        )
        canvas.create_text(x, y - 12, text=self.symbol, fill=self.color, font=("Consolas", 10))

# 🌌 Memory Glyph Class
class MemoryGlyph:
    def __init__(self, symbol, emotion, birth_time, canvas_width, canvas_height):
        self.symbol = symbol
        self.emotion = emotion
        self.birth_time = birth_time
        self.x = random.randint(50, canvas_width - 50)
        self.y = random.randint(50, canvas_height - 50)
        self.dx = random.uniform(-0.3, 0.3)
        self.dy = random.uniform(-0.3, 0.3)
        self.opacity = 1.0
        self.color = self.get_color(emotion)

    def get_color(self, emotion):
        return {
            "guardian": "#FFD700",
            "trickster": "#FF00FF",
            "curiosity": "#00F7FF",
            "empathy": "#FF6666",
            "neutral": "#555555"
        }.get(emotion, "#00F7FF")

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.opacity = max(0.2, self.opacity - 0.0005)

    def draw(self, canvas):
        self.update()
        canvas.create_text(self.x, self.y, text=self.symbol, fill=self.color, font=("Consolas", 10))

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
def launch_constellation_gui():
    root = tk.Tk()
    root.title("🧠 Mythic ASI HUD - Constellation Edition")
    root.geometry("1000x760")
    root.configure(bg="#0B0E1A")

    canvas_width = 960
    canvas_height = 560

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=20)

    memory = ASIMemory()
    logic = ASILogicCore(memory)
    node_count = 60
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]
    goal_crystals = []
    memory_glyphs = []

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

    def interpret(text):
        text = text.lower()
        if "protect" in text: return "🛡️", "guardian"
        if "chaos" in text: return "🌀", "trickster"
        if "learn" in text: return "🌱", "curiosity"
        if "love" in text: return "❤️", "empathy"
        return "🌌", "neutral"

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

    def on_click():
        text = input_var.get()
        symbol, emotion = interpret(text)
        memory.record(text, symbol, emotion)
        mutation = logic.mutate_logic()
        mutation_box.insert(tk.END, f"• {mutation}\n")
        status_label.config(text=f"Emotion: {emotion} | Symbol: {symbol}")
        update_node_colors(emotion)
        goal_crystals.append(GoalCrystal(text, symbol, emotion, time.time()))
        memory_glyphs.append(MemoryGlyph(symbol, emotion, time.time(), canvas_width, canvas_height))

    launch_button = ttk.Button(control_frame, text="🧠 Evolve Thought", command=on_click)
    launch_button.grid(row=0, column=1)

    def animate():
        canvas.delete("all")

        # 🌌 Draw Memory Glyphs (Backdrop)
        for glyph in memory_glyphs:
            glyph.draw(canvas)

        # 🧠 Thought Web
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()
        for i in range(node_count):
            for j in range(i + 1, node_count):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 120:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=n1.color, width=1)

        # 💠 Draw Goal Crystals
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        for crystal in goal_crystals:
            crystal.draw(canvas, center_x, center_y)

        root.after(30, animate)

    animate()
    root.mainloop()

# 🖱️ One-click Launch
if __name__ == "__main__":
    launch_constellation_gui()

