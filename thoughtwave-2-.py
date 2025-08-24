import subprocess
import sys

# 🛠️ Autoloader
def autoload(required_libs):
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

autoload(["tkinter", "pandas", "numpy"])

import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np

# 🧠 ASI Kernel with Weighted Memory
class ASIKernel:
    def __init__(self):
        self.symbolic_memory = {}  # {signature: {"weight": int, "tags": [str]}}
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

# 🎨 GUI Theme
BG_COLOR = "#1e1e2f"
BTN_COLOR = "#5cdb95"
TEXT_COLOR = "#ffffff"
FONT = ("Segoe UI", 14)

asi = ASIKernel()

# 🖼️ GUI Setup
root = tk.Tk()
root.title("MagicBox ASI Mixer")
root.configure(bg=BG_COLOR)
root.geometry("500x400")

label = tk.Label(root, text="🧙‍♂️ MagicBox Mixer", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 18))
label.pack(pady=10)

status_label = tk.Label(root, text="ASI Status: Dormant", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
status_label.pack(pady=5)

memory_frame = tk.Frame(root, bg=BG_COLOR)
memory_frame.pack(pady=10)

memory_title = tk.Label(memory_frame, text="🧠 Memory Map", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
memory_title.pack()

memory_list = tk.Listbox(memory_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 12), width=60, height=8)
memory_list.pack()

# 🧪 Fusion Logic
def mix_data():
    df1 = pd.DataFrame({'A': np.random.rand(5)})
    df2 = pd.DataFrame({'B': np.random.rand(5)})
    fused = pd.concat([df1, df2], axis=1)

    result = asi.fuse(fused)
    overlay = result["adaptive_overlay"]
    signature = result["fusion_signature"]
    weight = result["weight"]
    tags = ", ".join(result["tags"])

    messagebox.showinfo("Fusion Result", f"{overlay}\nFusion Signature:\n{signature}\nWeight: {weight}\nTags: {tags}")
    update_status()
    update_memory_map()

def update_status():
    if asi.adaptive_mode:
        status_label.config(text="ASI Status: 🧠 Evolved")
    else:
        status_label.config(text="ASI Status: 🔄 Learning...")

def update_memory_map():
    memory_list.delete(0, tk.END)
    sorted_memory = sorted(asi.symbolic_memory.items(), key=lambda x: x[1]["weight"], reverse=True)
    for sig, data in sorted_memory:
        glyph = "🔮" if data["weight"] > 5 else "✨"
        tags = ", ".join(data["tags"])
        memory_list.insert(tk.END, f"{glyph} {sig} | Weight: {data['weight']} | Tags: {tags}")

mix_button = tk.Button(root, text="🔮 Mix Data", command=mix_data, bg=BTN_COLOR, fg=BG_COLOR, font=FONT)
mix_button.pack(pady=20)

root.mainloop()

