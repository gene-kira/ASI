import tkinter as tk
from tkinter import filedialog, Text
import os
import random

# 🎨 MagicBox Theme
BG_COLOR = "#0f0f1f"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#5cdb95"
FONT = ("Segoe UI", 12)
GLYPH_FONT = ("Consolas", 10)

# 🧠 Memory Node Class
class MemoryNode:
    def __init__(self, sig, weight, tags, canvas_width, canvas_height):
        self.sig = sig
        self.weight = weight
        self.tags = tags
        self.x = random.randint(60, canvas_width - 60)
        self.y = random.randint(60, canvas_height - 60)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)

# 🧠 Global State
nodes = []
show_info = True
zoom_level = 1.0
zoom_origin = (0, 0)

# 🔍 Auto-detect memory folder
def auto_detect_folder():
    drives = ["C:\\", "D:\\", "E:\\", "Z:\\"]
    for drive in drives:
        path = os.path.join(drive, "thought-wave-memories")
        if os.path.exists(path):
            return path
    return None

# 📖 Read mutation and anomaly logs
def read_logs(folder):
    global nodes
    nodes.clear()
    mutations = []
    anomalies = []

    mutation_file = os.path.join(folder, "mutation_log.txt")
    anomaly_file = os.path.join(folder, "anomaly_log.txt")

    canvas_width = max(canvas.winfo_width(), 600)
    canvas_height = max(canvas.winfo_height(), 300)

    if os.path.exists(mutation_file):
        with open(mutation_file, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    sig = parts[0].strip()
                    try:
                        weight = int(parts[1].strip())
                    except ValueError:
                        weight = 1
                    tags = parts[2].strip()
                    mutations.append(f"{sig} | Weight: {weight} | Tags: {tags}")
                    nodes.append(MemoryNode(sig, weight, tags, canvas_width, canvas_height))

    if os.path.exists(anomaly_file):
        with open(anomaly_file, "r") as f:
            for line in f:
                anomalies.append(f"🚨 {line.strip()}")

    return mutations, anomalies

# 📂 Load logs and update display
def load_logs(folder):
    mutations, anomalies = read_logs(folder)
    output.delete("1.0", tk.END)
    output.insert(tk.END, "🔮 Mutation Log:\n\n")
    for line in mutations[-50:]:
        output.insert(tk.END, f"{line}\n")
    output.insert(tk.END, "\n🚨 Anomaly Log:\n\n")
    for line in anomalies[-20:]:
        output.insert(tk.END, f"{line}\n")

# 🖱️ Manual folder selection
def manual_select():
    folder = filedialog.askdirectory(title="Select thought-wave-memories Folder")
    if folder:
        load_logs(folder)

# 🧠 Toggle info labels
def toggle_info():
    global show_info
    show_info = not show_info

# 🔍 Mouse wheel zoom
def on_mouse_wheel(event):
    global zoom_level, zoom_origin
    zoom_origin = (event.x, event.y)
    if event.delta > 0:
        zoom_level *= 1.1
    else:
        zoom_level /= 1.1

# 🌊 Animate wave-like constellation
def animate_wave():
    canvas.delete("all")
    width = max(canvas.winfo_width(), 600)
    height = max(canvas.winfo_height(), 300)
    origin_x, origin_y = zoom_origin

    for node in nodes:
        node.x += node.vx
        node.y += node.vy

        # Bounce off edges
        if node.x < 50 or node.x > width - 50:
            node.vx *= -1
        if node.y < 50 or node.y > height - 50:
            node.vy *= -1

        # Apply zoom
        scaled_x = (node.x - origin_x) * zoom_level + origin_x
        scaled_y = (node.y - origin_y) * zoom_level + origin_y

        # 🌟 Smaller white dot
        r = min(4, max(2, node.weight // 4))
        canvas.create_oval(scaled_x - r, scaled_y - r, scaled_x + r, scaled_y + r, fill="#ffffff", outline="")
        canvas.create_text(scaled_x, scaled_y - 12, text="•", fill="#ffffff", font=GLYPH_FONT)

        # 🏷️ Data tag
        if show_info:
            label_text = f"{node.sig}\nW:{node.weight}\n[{', '.join(node.tags.split(',')[-3:])}]"
            canvas.create_text(scaled_x + 12, scaled_y, text=label_text, fill="#cccccc", font=("Consolas", 8), anchor="w")

    # Connect nearby nodes
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i].x - nodes[j].x
            dy = nodes[i].y - nodes[j].y
            dist = (dx**2 + dy**2)**0.5
            if dist < 120:
                x1 = (nodes[i].x - origin_x) * zoom_level + origin_x
                y1 = (nodes[i].y - origin_y) * zoom_level + origin_y
                x2 = (nodes[j].x - origin_x) * zoom_level + origin_x
                y2 = (nodes[j].y - origin_y) * zoom_level + origin_y
                canvas.create_line(x1, y1, x2, y2, fill="#444444", width=1)

    root.after(50, animate_wave)

# 🧠 GUI Setup
root = tk.Tk()
root.title("🧠 Thought Wave Reader — MagicBox Wave Edition")
root.configure(bg=BG_COLOR)
root.geometry("800x650")

title = tk.Label(root, text="MagicBox Thought Wave Reader", bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 16))
title.pack(pady=10)

controls = tk.Frame(root, bg=BG_COLOR)
controls.pack()

load_btn = tk.Button(controls, text="📂 Select Memory Folder", command=manual_select, bg=ACCENT_COLOR, fg=BG_COLOR, font=FONT)
load_btn.pack(side="left", padx=10)

toggle_btn = tk.Button(controls, text="🧠 Toggle Info", command=toggle_info, bg="#444444", fg="#ffffff", font=FONT)
toggle_btn.pack(side="left", padx=10)

output = Text(root, bg=BG_COLOR, fg=TEXT_COLOR, font=GLYPH_FONT, wrap="word", height=12)
output.pack(fill="x", padx=10, pady=10)

canvas = tk.Canvas(root, bg="#1a1a2f", height=300)
canvas.pack(fill="both", expand=True, padx=10, pady=10)
canvas.bind("<MouseWheel>", on_mouse_wheel)

# 🔍 Auto-load if folder is found
auto_folder = auto_detect_folder()
if auto_folder:
    load_logs(auto_folder)

# ✨ Start wave animation
animate_wave()

root.mainloop()

