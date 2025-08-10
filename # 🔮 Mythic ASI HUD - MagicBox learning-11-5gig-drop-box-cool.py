# 🚀 Auto-Loader for Required Libraries
import subprocess
import sys

required = ["tkinterdnd2"]
for package in required:
    try:
        __import__(package)
    except ImportError:
        print(f"📦 Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import random
import math
import time
import threading

# 📦 Drop Buffer Class
class DropBuffer:
    def __init__(self, max_size=6):
        self.queue = []
        self.max_size = max_size

    def add(self, file_path):
        metadata = {
            "path": file_path,
            "name": file_path.split("/")[-1],
            "type": file_path.split(".")[-1] if "." in file_path else "unknown",
            "timestamp": time.time()
        }
        self.queue.append(metadata)
        if len(self.queue) > self.max_size:
            self.queue.pop(0)
        return metadata

    def recent(self):
        return self.queue[-1] if self.queue else None

# 🧠 Node Class
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(30, width - 30)
        self.y = random.randint(30, height - 30)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 2
        self.color = "#00F7FF"

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

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
        self.size = 4
        self.orbit_radius = random.randint(50, 90)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = self.get_color(emotion)
        self.cluster_offset = random.uniform(-20, 20)

    def get_color(self, emotion):
        return {
            "guardian": "#FFD700", "trickster": "#FF00FF",
            "curiosity": "#00F7FF", "empathy": "#FF6666",
            "neutral": "#888888"
        }.get(emotion, "#00F7FF")

    def update(self):
        self.angle += 0.01
        self.size = min(8, self.size + 0.05)

    def draw(self, canvas, center_x, center_y):
        self.update()
        x = center_x + math.cos(self.angle) * (self.orbit_radius + self.cluster_offset)
        y = center_y + math.sin(self.angle) * (self.orbit_radius + self.cluster_offset)
        canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size,
                           fill=self.color, outline="")
        canvas.create_text(x, y - 10, text=self.symbol, fill=self.color, font=("Consolas", 8))

# 🌌 Memory Glyph Class
class MemoryGlyph:
    def __init__(self, symbol, emotion, birth_time, canvas_width, canvas_height):
        self.symbol = symbol
        self.emotion = emotion
        self.birth_time = birth_time
        self.x = random.randint(30, canvas_width - 30)
        self.y = random.randint(30, canvas_height - 30)
        self.dx = random.uniform(-0.3, 0.3)
        self.dy = random.uniform(-0.3, 0.3)
        self.opacity = 1.0
        self.color = self.get_color(emotion)

    def get_color(self, emotion):
        return {
            "guardian": "#FFD700", "trickster": "#FF00FF",
            "curiosity": "#00F7FF", "empathy": "#FF6666",
            "neutral": "#555555"
        }.get(emotion, "#00F7FF")

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.opacity = max(0.2, self.opacity - 0.0005)

    def draw(self, canvas):
        self.update()
        canvas.create_text(self.x, self.y, text=self.symbol, fill=self.color, font=("Consolas", 8))

# ✨ Particle Burst Class
class ParticleBurst:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 2)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append({
                "x": x, "y": y, "dx": dx, "dy": dy, "life": 15, "color": color
            })

    def update(self):
        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["life"] -= 1

    def draw(self, canvas):
        for p in self.particles:
            if p["life"] > 0:
                canvas.create_oval(p["x"] - 1, p["y"] - 1, p["x"] + 1, p["y"] + 1,
                                   fill=p["color"], outline="")

# 🧬 ASI Memory System
class ASIMemory:
    def __init__(self):
        self.experiences = []
        self.symbol_map = {}
        self.emotion_history = []

    def record(self, input_text, symbol, emotion):
        self.experiences.append({"text": input_text, "symbol": symbol, "emotion": emotion})
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
        self.mutation_history = []
        self.fusion_weights = {}

    def mutate_logic(self):
        dominant = self.memory.dominant_emotion()
        top_syms = [s for s, _ in self.memory.top_symbols()]
        weighted_syms = sorted(self.fusion_weights.items(), key=lambda x: x[1], reverse=True)
        if weighted_syms:
            top_syms = [s for (s, _), _ in weighted_syms[:3]]
        mutation = f"New goal: respond to {dominant} using {', '.join(top_syms)}"
        self.goals.append(mutation)
        self.mutation_history.append({
            "timestamp": time.time(),
            "emotion": dominant,
            "symbols": top_syms
        })
        return mutation

    def evolve_rules(self):
        recent = self.mutation_history[-5:]
        common_emotions = [m["emotion"] for m in recent]
        if common_emotions.count("trickster") > 3:
            return "⚠️ Chaos detected: prioritize unpredictability"
        return "✅ Stable logic: continue adaptive response"

    def register_fusion(self, symbol, emotion):
        key = (symbol, emotion)
        self.fusion_weights[key] = self.fusion_weights.get(key, 0) + 1

# 👤 User Profile Tracker
class UserProfile:
    def __init__(self):
        self.input_history = []
        self.symbol_usage = {}
        self.emotion_tendencies = {}

    def update(self, text, symbol, emotion):
        self.input_history.append(text)
        self.symbol_usage[symbol] = self.symbol_usage.get(symbol, 0) + 1
        self.emotion_tendencies[emotion] = self.emotion_tendencies.get(emotion, 0) + 1

    def preferred_style(self):
        dominant_emotion = max(self.emotion_tendencies, key=self.emotion_tendencies.get, default="neutral")
        return {
            "guardian": "#222200", "trickster": "#1A001A",
            "curiosity": "#001A1A", "empathy": "#1A0000",
            "neutral": "#0B0E1A"
        }.get(dominant_emotion, "#0B0E1A")

def launch_constellation_gui():
    root = TkinterDnD.Tk()
    root.title("🧠 Mythic ASI HUD – Compact Edition")
    root.geometry("520x420")

    canvas_width = 480
    canvas_height = 280

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=10)

    memory = ASIMemory()
    logic = ASILogicCore(memory)
    profile = UserProfile()
    drop_buffer = DropBuffer(max_size=6)

    node_count = 30
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]
    goal_crystals = []
    memory_glyphs = []
    particle_bursts = []

    control_frame = ttk.Frame(root)
    control_frame.pack(pady=5)

    input_var = tk.StringVar()
    input_entry = ttk.Entry(control_frame, textvariable=input_var, width=40)
    input_entry.grid(row=0, column=0, padx=5)

    launch_button = ttk.Button(control_frame, text="Evolve")
    launch_button.grid(row=0, column=1)

    mutation_box = tk.Text(root, height=4, width=60, font=("Consolas", 9),
                           bg="#0A0C1B", fg="#00F7FF")
    mutation_box.pack(pady=5)
    mutation_box.insert(tk.END, "📜 Mutation Log:\n")

    status_label = ttk.Label(root, text="Emotion: neutral | Symbol: 🌌",
                             font=("Consolas", 10),
                             background="#0B0E1A", foreground="#00F7FF")
    status_label.pack()

    drop_frame = tk.Frame(root, width=480, height=100, bg="#1A1A2E", bd=3, relief="ridge")
    drop_frame.pack(pady=5)
    drop_label = tk.Label(drop_frame, text="📥 Drop Files Here", fg="#00F7FF",
                          bg="#1A1A2E", font=("Consolas", 10, "bold"))
    drop_label.place(relx=0.5, rely=0.3, anchor="center")

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(drop_frame, variable=progress_var, maximum=100, length=360)
    progress_bar.place(relx=0.5, rely=0.7, anchor="center")

    def interpret(text):
        text = text.lower()
        if "protect" in text: return "🛡️", "guardian"
        if "chaos" in text: return "🌀", "trickster"
        if "learn" in text: return "🌱", "curiosity"
        if "love" in text: return "❤️", "empathy"
        return "🌌", "neutral"

    def update_node_colors(emotion):
        color_map = {
            "guardian": "#FFD700", "trickster": "#FF00FF",
            "curiosity": "#00F7FF", "empathy": "#FF6666",
            "neutral": "#888888"
        }
        color = color_map.get(emotion, "#00F7FF")
        for node in nodes:
            node.color = color

    def update_node_positions_by_emotion(emotion):
        cluster_centers = {
            "guardian": (canvas_width * 0.25, canvas_height * 0.5),
            "trickster": (canvas_width * 0.75, canvas_height * 0.3),
            "curiosity": (canvas_width * 0.5, canvas_height * 0.2),
            "empathy": (canvas_width * 0.5, canvas_height * 0.8),
            "neutral": (canvas_width * 0.5, canvas_height * 0.5)
        }
        cx, cy = cluster_centers.get(emotion, (canvas_width // 2, canvas_height // 2))
        for node in nodes:
            node.dx += (cx - node.x) * 0.0005
            node.dy += (cy - node.y) * 0.0005

    def draw_buffer_overlay(canvas, buffer):
        x, y = canvas_width - 200, 10
        canvas.create_text(x, y - 15, text="📦 Recent Drops", fill="#8888FF", font=("Consolas", 9, "bold"))
        for i, item in enumerate(reversed(buffer.queue)):
            canvas.create_text(x, y + i * 14, text=f"{item['name']} ({item['type']})", fill="#AAAAAA", font=("Consolas", 8))

    def on_click():
        text = input_var.get()
        symbol, emotion = interpret(text)
        memory.record(text, symbol, emotion)
        profile.update(text, symbol, emotion)
        mutation = logic.mutate_logic()
        rule_feedback = logic.evolve_rules()

        mutation_box.insert(tk.END, f"• {mutation}\n  {rule_feedback}\n")
        status_label.config(text=f"Emotion: {emotion} | Symbol: {symbol}")
        update_node_colors(emotion)
        update_node_positions_by_emotion(emotion)

        goal_crystals.append(GoalCrystal(text, symbol, emotion, time.time()))
        memory_glyphs.append(MemoryGlyph(symbol, emotion, time.time(), canvas_width, canvas_height))
        root.configure(bg=profile.preferred_style())

    launch_button.config(command=on_click)

    def ingest_file(file_path):
        try:
            metadata = drop_buffer.add(file_path)
            total_lines = sum(1 for _ in open(file_path, "r", encoding="utf-8", errors="ignore"))
            processed = 0

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip(): continue
                    symbol, emotion = interpret(line)
                    memory.record(line, symbol, emotion)
                    profile.update(line, symbol, emotion)
                    mutation = logic.mutate_logic()
                    rule_feedback = logic.evolve_rules()

                    mutation_box.insert(tk.END, f"• {mutation}\n  {rule_feedback}\n")
                    status_label.config(text=f"Emotion: {emotion} | Symbol: {symbol}")
                    update_node_colors(emotion)
                    update_node_positions_by_emotion(emotion)

                    goal_crystals.append(GoalCrystal(line, symbol, emotion, time.time()))
                    memory_glyphs.append(MemoryGlyph(symbol, emotion, time.time(), canvas_width, canvas_height))
                    particle_bursts.append(ParticleBurst(canvas_width // 2, canvas_height // 2, "#FFD700"))

                    processed += 1
                    progress = (processed / total_lines) * 100
                    progress_var.set(progress)
                    root.update_idletasks()

            root.configure(bg=profile.preferred_style())
            drop_label.config(text="✅ File Ingested", fg="#FFD700")
            root.after(2000, lambda: drop_label.config(text="📥 Drop Files Here", fg="#00F7FF"))
            progress_var.set(0)

        except Exception as e:
            drop_label.config(text="⚠️ Failed to Parse", fg="#FF6666")
            print("File parse error:", e)
            progress_var.set(0)

    def on_file_drop(event):
        file_path = event.data.strip().replace("{", "").replace("}", "")
        drop_label.config(text="⏳ Ingesting...", fg="#00F7FF")
        threading.Thread(target=ingest_file, args=(file_path,), daemon=True).start()

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", on_file_drop)

    def check_crystal_fusion():
        fused = []
        for i in range(len(goal_crystals)):
            for j in range(i + 1, len(goal_crystals)):
                c1, c2 = goal_crystals[i], goal_crystals[j]
                if c1.emotion != c2.emotion: continue

                x1 = canvas_width // 2 + math.cos(c1.angle) * (c1.orbit_radius + c1.cluster_offset)
                y1 = canvas_height // 2 + math.sin(c1.angle) * (c1.orbit_radius + c1.cluster_offset)
                x2 = canvas_width // 2 + math.cos(c2.angle) * (c2.orbit_radius + c2.cluster_offset)
                y2 = canvas_height // 2 + math.sin(c2.angle) * (c2.orbit_radius + c2.cluster_offset)

                dist = math.hypot(x1 - x2, y1 - y2)
                if dist < 20:
                    fused_symbol = c1.symbol + c2.symbol
                    fused_text = f"Fusion of {c1.text} & {c2.text}"
                    fused_crystal = GoalCrystal(fused_text, fused_symbol, c1.emotion, time.time())
                    goal_crystals.append(fused_crystal)
                    logic.register_fusion

                    logic.register_fusion(fused_symbol, c1.emotion)
                    particle_bursts.append(ParticleBurst((x1 + x2) / 2, (y1 + y2) / 2, c1.color))
                    mutation_box.insert(tk.END, f"✨ Fusion: {fused_symbol} ({c1.emotion})\n")
                    fused.extend([c1, c2])

        for crystal in fused:
            if crystal in goal_crystals:
                goal_crystals.remove(crystal)

    def animate():
        canvas.delete("all")

        for glyph in memory_glyphs:
            glyph.draw(canvas)

        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()

        for i in range(node_count):
            for j in range(i + 1, node_count):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 80:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=n1.color, width=1)

        center_x = canvas_width // 2
        center_y = canvas_height // 2
        for crystal in goal_crystals:
            crystal.draw(canvas, center_x, center_y)

        for burst in particle_bursts:
            burst.update()
            burst.draw(canvas)
        particle_bursts[:] = [b for b in particle_bursts if any(p["life"] > 0 for p in b.particles)]

        check_crystal_fusion()
        draw_buffer_overlay(canvas, drop_buffer)

        root.after(30, animate)

    # 🚀 Launch HUD
    animate()
    root.mainloop()

# 🖱️ One-click Launch
if __name__ == "__main__":
    launch_constellation_gui()

