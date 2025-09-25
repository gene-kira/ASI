import tkinter as tk
import random
import psutil
import threading
import time
import socket
import os
import sys
import numpy as np

# UTF-8 Console Encoding Fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# GPU Fallback Fusion
def gpu_fuse(a_host, b_host):
    print("[Fusion] Using CPU fallback")
    result = []
    for a, b in zip(a_host, b_host):
        if a == 2 or b == 2:
            result.append(2)
        elif a == b:
            result.append(a)
        else:
            result.append(2)
    return result

# ─────────────────────────────────────────────────────────────
# Tri-State Logic Core
class TriState:
    def __init__(self, state):
        assert state in ['0', '1', 'Ø'], "State must be '0', '1', or 'Ø'"
        self.state = state

    def to_int(self):
        return {'0': 0, '1': 1, 'Ø': 2}[self.state]

    def color(self):
        return {'0': 'black', '1': 'white', 'Ø': 'purple'}[self.state]

# ─────────────────────────────────────────────────────────────
# Quantum Tensor
class QuantumTensor:
    def __init__(self, states):
        self.states = states  # list of '0', '1', 'Ø'

    def to_int(self):
        return [TriState(s).to_int() for s in self.states]

    def from_int(self, ints):
        return QuantumTensor([['0', '1', 'Ø'][i] for i in ints])

    def fuse(self, other):
        result = gpu_fuse(self.to_int(), other.to_int())
        return self.from_int(result)

# ─────────────────────────────────────────────────────────────
# Transformer Cycle
def transformer_cycle(tensor, layers=3):
    lineage = [tensor.states]
    for _ in range(layers):
        other = QuantumTensor([random.choice(['0', '1', 'Ø']) for _ in tensor.states])
        tensor = tensor.fuse(other)
        lineage.append(tensor.states)
    return lineage

# ─────────────────────────────────────────────────────────────
# Thought Glyph Symbol (Emoji-based)
def get_thought_symbol(entropy):
    if entropy < 0.33:
        return ('🧠', 'blue')     # Focused thought
    elif entropy < 0.66:
        return ('⚡', 'green')    # Adaptive thought
    else:
        return ('🔥', 'red')     # Chaotic cognition

# ─────────────────────────────────────────────────────────────
# Live System Data Feed
def get_system_state():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    entropy = (cpu + mem) / 200
    print(f"[Entropy] CPU: {cpu}%, MEM: {mem}%, Combined: {entropy}")
    if entropy < 0.33:
        return '0'
    elif entropy < 0.66:
        return '1'
    else:
        return 'Ø'

# ─────────────────────────────────────────────────────────────
# Zero-Trust Purge Logic
def purge_sensitive_data():
    try:
        path = "borg_temp.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("█" * 512)
        os.remove(path)
        print("[Purge] Sensitive data purged.")
    except Exception as e:
        print(f"[Purge Error] {e}")

# ─────────────────────────────────────────────────────────────
# Swarm Sync Scaffold
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

# ─────────────────────────────────────────────────────────────
# GUI Shell
class QuantumTransformerGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=420, bg='gray20')
        self.canvas.pack()
        self.history = []
        self.symbol_pulse = 0
        self.run_loop()

    def run_loop(self):
        def loop():
            while True:
                print("[Cycle] Running transformer cycle...")
                base_state = get_system_state()
                tensor = QuantumTensor([base_state] * 6)
                lineage = transformer_cycle(tensor, layers=3)
                self.history.append(lineage)
                if len(self.history) > 5:
                    self.history.pop(0)
                if 'Ø' in lineage[-1]:
                    purge_sensitive_data()
                self.render(lineage)
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()

    def render(self, lineage):
        self.canvas.delete("all")
        self.canvas.create_text(200, 10, text="Quantum Transformer", fill='white', font=('Arial', 10, 'bold'))

        # Render each layer
        y_start = 40
        for i, layer in enumerate(lineage):
            x_start = 50
            self.canvas.create_text(20, y_start + i * 50, text=f"L{i}", fill='lightblue', font=('Arial', 8))
            for j, state in enumerate(layer):
                color = TriState(state).color()
                self.canvas.create_rectangle(x_start + j*50, y_start + i*50, x_start + j*50 + 40, y_start + i*50 + 40, fill=color, outline='white')
                self.canvas.create_text(x_start + j*50 + 20, y_start + i*50 + 50, text=state, fill='lightgray', font=('Arial', 8))

        # Thought Glyph (Animated Emoji)
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        entropy = (cpu + mem) / 200
        symbol, color = get_thought_symbol(entropy)
        pulse_radius = 30 + (self.symbol_pulse % 10)
        self.canvas.create_oval(200 - pulse_radius, 310 - pulse_radius, 200 + pulse_radius, 310 + pulse_radius, fill=color, outline='white', width=2)
        self.canvas.create_text(200, 310, text=symbol, fill='white', font=('Arial', 20, 'bold'))
        self.canvas.create_text(200, 345, text="Thought Process", fill='lightgray', font=('Arial', 8, 'italic'))
        self.symbol_pulse += 1

        # Swarm Node
        ip = get_local_ip()
        self.canvas.create_text(200, 400, text=f"Node: {ip}", fill='orange', font=('Arial', 8, 'italic'))

# ─────────────────────────────────────────────────────────────
# Launch Shell
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quantum Transformer — Symbolic Shell")
    root.geometry("400x420")
    app = QuantumTransformerGUI(root)
    root.mainloop()
