import tkinter as tk
import random
import psutil
import threading
import time
import socket
import os
import sys

# UTF-8 Console Encoding Fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')

# Extended Symbolic Logic Core
class SymbolicState:
    def __init__(self, state):
        assert state in ['0', '1', 'Ø', '⊗', '⨂'], "Invalid symbolic state"
        self.state = state

    def mutate(self, other):
        if '⨂' in [self.state, other.state]:
            return SymbolicState('⨂')
        elif '⊗' in [self.state, other.state]:
            return SymbolicState('⊗')
        elif 'Ø' in [self.state, other.state]:
            return SymbolicState('Ø')
        elif self.state == other.state:
            return SymbolicState(self.state)
        else:
            return SymbolicState('Ø')

    def color(self):
        return {'0': 'black', '1': 'white', 'Ø': 'purple', '⊗': 'red', '⨂': 'gold'}[self.state]

    def narrate(self):
        return {
            '0': "Void detected.",
            '1': "Signal active.",
            'Ø': "Fusion achieved.",
            '⊗': "Quantum burst: 1B ops simulated.",
            '⨂': "Quantum singularity: 1,280T teraflops engaged."
        }[self.state]

# Live System Data Feed
def get_system_state():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    entropy = (cpu + mem) / 200
    if entropy < 0.2:
        return SymbolicState('0')
    elif entropy < 0.4:
        return SymbolicState('1')
    elif entropy < 0.6:
        return SymbolicState('Ø')
    elif entropy < 0.8:
        return SymbolicState('⊗')
    else:
        return SymbolicState('⨂')

# Zero-Trust Purge Logic
def purge_sensitive_data():
    try:
        path = "borg_temp.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("█" * 512)
        os.remove(path)
    except Exception as e:
        print(f"[Purge Error] {e}")

# Symbolic Memory Pattern
def generate_memory_pattern():
    return [random.choice(['0', '1', 'Ø', '⊗', '⨂']) for _ in range(6)]

def render_memory_pattern(canvas, pattern):
    x_start = 50
    y = 280
    for i, state in enumerate(pattern):
        color = {'0': 'black', '1': 'white', 'Ø': 'purple', '⊗': 'red', '⨂': 'gold'}[state]
        canvas.create_oval(x_start + i*50, y, x_start + i*50 + 40, y + 40, fill=color, outline='gray')
        cx = x_start + i*50 + 20
        cy = y + 20
        if state == '⊗':
            canvas.create_line(cx - 10, cy - 10, cx + 10, cy + 10, fill='white', width=2)
            canvas.create_line(cx + 10, cy - 10, cx - 10, cy + 10, fill='white', width=2)
        elif state == '⨂':
            canvas.create_line(cx - 12, cy - 12, cx + 12, cy + 12, fill='white', width=2)
            canvas.create_line(cx + 12, cy - 12, cx - 12, cy + 12, fill='white', width=2)
            canvas.create_line(cx - 8, cy - 12, cx + 8, cy + 12, fill='white', width=1)
            canvas.create_line(cx + 8, cy - 12, cx - 8, cy + 12, fill='white', width=1)
        canvas.create_text(cx, y + 50, text=state, fill='lightgray', font=('Consolas', 8))

# Swarm Sync Scaffold
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

# GUI Shell
class BorgAssimilationGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=350, bg='gray10')
        self.canvas.pack()
        self.history = []
        self.memory_pattern = generate_memory_pattern()
        self.run_loop()

    def run_loop(self):
        def loop():
            while True:
                a = get_system_state()
                b = SymbolicState(random.choice(['0', '1', 'Ø', '⊗', '⨂']))
                fusion = a.mutate(b)
                self.history.append((a, b, fusion))
                if len(self.history) > 8:
                    self.history.pop(0)
                if fusion.state in ['Ø', '⊗', '⨂']:
                    purge_sensitive_data()
                self.memory_pattern = generate_memory_pattern()
                self.render(a, b, fusion)
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()

    def render(self, a, b, fusion):
        self.canvas.delete("all")
        # Nodes
        self.canvas.create_oval(40, 40, 100, 100, fill=a.color(), outline='cyan', width=1)
        self.canvas.create_text(70, 110, text=f"A: {a.state}", fill='cyan', font=('Consolas', 9))
        self.canvas.create_text(70, 125, text=a.narrate(), fill='lightblue', font=('Consolas', 7))

        self.canvas.create_oval(300, 40, 360, 100, fill=b.color(), outline='magenta', width=1)
        self.canvas.create_text(330, 110, text=f"B: {b.state}", fill='magenta', font=('Consolas', 9))
        self.canvas.create_text(330, 125, text=b.narrate(), fill='pink', font=('Consolas', 7))

        self.canvas.create_oval(170, 160, 230, 220, fill=fusion.color(), outline='yellow', width=2)
        cx, cy = 200, 190
        if fusion.state == '⊗':
            self.canvas.create_line(cx - 10, cy - 10, cx + 10, cy + 10, fill='white', width=2)
            self.canvas.create_line(cx + 10, cy - 10, cx - 10, cy + 10, fill='white', width=2)
        elif fusion.state == '⨂':
            self.canvas.create_line(cx - 12, cy - 12, cx + 12, cy + 12, fill='white', width=2)
            self.canvas.create_line(cx + 12, cy - 12, cx - 12, cy + 12, fill='white', width=2)
            self.canvas.create_line(cx - 8, cy - 12, cx + 8, cy + 12, fill='white', width=1)
            self.canvas.create_line(cx + 8, cy - 12, cx - 8, cy + 12, fill='white', width=1)
        self.canvas.create_text(200, 230, text=f"Fusion: {fusion.state}", fill='yellow', font=('Consolas', 10, 'bold'))
        self.canvas.create_text(200, 245, text=fusion.narrate(), fill='gold', font=('Consolas', 8))

        # Mutation History
        y = 10
        self.canvas.create_text(200, y, text="Lineage", fill='white', font=('Consolas', 10, 'underline'))
        for i, (s1, s2, f) in enumerate(reversed(self.history)):
            y += 15
            lineage = f"{s1.state}+{s2.state}→{f.state}"
            self.canvas.create_text(200, y, text=lineage, fill='lightgray',         font=('Consolas', 8))

        # Memory Pattern
        self.canvas.create_text(200, 270, text="Memory Pattern", fill='lightgreen', font=('Consolas', 9, 'underline'))
        render_memory_pattern(self.canvas, self.memory_pattern)

        # Swarm Node
        ip = get_local_ip()
        self.canvas.create_text(200, 335, text=f"Node: {ip}", fill='orange', font=('Consolas', 8, 'italic'))

# Launch Shell
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Borg Assimilation — Quantum Singularity Shell")
    root.geometry("400x350")
    app = BorgAssimilationGUI(root)
    root.mainloop()


