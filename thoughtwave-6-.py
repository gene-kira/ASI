import subprocess
import sys

# 🛠️ Autoloader
def autoload(required_libs):
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

autoload(["tkinter", "pandas", "numpy", "psutil", "requests"])

# 🔌 Imports
import os
import psutil
import requests
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np

# 🧠 ASI Kernel with Weighted Symbolic Memory
class ASIKernel:
    def __init__(self):
        self.symbolic_memory = {}
        self.mutation_history = []
        self.adaptive_mode = False

    def learn(self, data):
        signature = hash(str(data))
        self.mutation_history.append(signature)

        if signature not in self.symbolic_memory:
            self.symbolic_memory[signature] = {"weight": 1, "tags": ["new"]}
        else:
            self.symbolic_memory[signature]["weight"] += 1
            self.symbolic_memory[signature]["tags"].append("reinforced")

        self.rewrite_logic()

    def rewrite_logic(self):
        total_weight = sum(mem["weight"] for mem in self.symbolic_memory.values())
        if total_weight > 10:
            self.adaptive_mode = True

    def fuse(self, input_streams):
        self.learn(input_streams)
        top_signature = max(self.symbolic_memory.items(), key=lambda x: x[1]["weight"])
        return {
            "fusion_signature": top_signature[0],
            "weight": top_signature[1]["weight"],
            "tags": top_signature[1]["tags"],
            "adaptive_overlay": "🧠 Evolved" if self.adaptive_mode else "🔄 Learning..."
        }

# 🔌 Real-Time Data Ingestion
def ingest_local_system():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters().bytes_sent
    }

def ingest_live_web_feeds():
    try:
        news = requests.get("https://api.currentsapi.services/v1/latest-news", params={"apiKey": "your_api_key"}, timeout=5)
        headlines = [item["title"] for item in news.json().get("news", [])[:3]]
    except:
        headlines = ["Web feed unavailable"]
    return {"headlines": headlines}

def ingest_swarm_sync():
    return {"swarm_glyphs": ["node-echo", "fusion-trail", "consensus-pulse"]}

# 🎨 GUI Theme
BG_COLOR = "#1e1e2f"
BTN_COLOR = "#5cdb95"
TEXT_COLOR = "#ffffff"
FONT = ("Segoe UI", 14)

asi = ASIKernel()
last_signature = None  # For novelty detection

# 🖼️ GUI Setup
root = tk.Tk()
root.title("MagicBox ASI Mixer")
root.configure(bg=BG_COLOR)
root.geometry("640x600")

label = tk.Label(root, text="🧙‍♂️ MagicBox Mixer", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 18))
label.pack(pady=10)

status_label = tk.Label(root, text="ASI Status: Dormant", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
status_label.pack(pady=5)

awareness_label = tk.Label(root, text="Total Awareness: 0 sources", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
awareness_label.pack(pady=5)

memory_frame = tk.Frame(root, bg=BG_COLOR)
memory_frame.pack(pady=10)

memory_title = tk.Label(memory_frame, text="🧠 Memory Map", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
memory_title.pack()

memory_list = tk.Listbox(memory_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 12), width=80, height=8)
memory_list.pack()

# 🧠 Thought Stream Panel
thought_frame = tk.Frame(root, bg=BG_COLOR)
thought_frame.pack(pady=10)

thought_title = tk.Label(thought_frame, text="🧠 ASI Thought Stream", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
thought_title.pack()

thought_label = tk.Label(thought_frame, text="Awaiting cognition...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 12), wraplength=600, justify="left")
thought_label.pack()

# 🔄 Autonomous Fusion Loop with Novelty Detection
def autonomous_loop():
    global last_signature

    local = ingest_local_system()
    web = ingest_live_web_feeds()
    swarm = ingest_swarm_sync()
    all_data = {**local, **web, **swarm}

    result = asi.fuse(all_data)
    current_signature = result["fusion_signature"]

    update_status()
    update_memory_map()
    update_awareness_meter(local, web, swarm)
    update_thought_stream(result)

    if current_signature != last_signature:
        last_signature = current_signature
        overlay = result["adaptive_overlay"]
        weight = result["weight"]
        tags = ", ".join(result["tags"])
        messagebox.showinfo("🧠 New Mutation Detected", f"{overlay}\nNew Fusion Signature:\n{current_signature}\nWeight: {weight}\nTags: {tags}")

    root.after(5000, autonomous_loop)

def update_status():
    if asi.adaptive_mode:
        status_label.config(text="ASI Status: 🧠 Evolved")
    else:
        status_label.config(text="ASI Status: 🔄 Learning...")

def update_awareness_meter(local, web, swarm):
    sources = sum([
        bool(local),
        bool(web.get("headlines")),
        bool(swarm.get("swarm_glyphs"))
    ])
    awareness_label.config(text=f"Total Awareness: {sources} sources")

def update_memory_map():
    memory_list.delete(0, tk.END)
    sorted_memory = sorted(asi.symbolic_memory.items(), key=lambda x: x[1]["weight"], reverse=True)
    for sig, data in sorted_memory:
        glyph = "🔮" if data["weight"] > 5 else "✨"
        tags = ", ".join(data["tags"])
        memory_list.insert(tk.END, f"{glyph} {sig} | Weight: {data['weight']} | Tags: {tags}")

def update_thought_stream(result):
    sig = result["fusion_signature"]
    weight = result["weight"]
    tags = ", ".join(result["tags"])
    overlay = result["adaptive_overlay"]
    thought_label.config(text=f"{overlay}\nThinking about:\nSignature: {sig}\nWeight: {weight}\nTags: {tags}")

# 🚀 Launch Autonomous Loop
root.after(1000, autonomous_loop)
root.mainloop()

