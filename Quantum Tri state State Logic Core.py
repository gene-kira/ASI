import tkinter as tk
import psutil
import threading
import time
import socket
import os
import sys

# ─────────────────────────────────────────────────────────────
# UTF-8 Console Encoding Fix
# ─────────────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# Tri-State Logic Core
# ─────────────────────────────────────────────────────────────
class TriState:
    def __init__(self, state):
        assert state in ['0', '1', 'Ø'], "State must be '0', '1', or 'Ø'"
        self.state = state

    def mutate(self, other):
        if self.state == 'Ø' or other.state == 'Ø':
            return TriState('Ø')
        elif self.state == other.state:
            return TriState(self.state)
        else:
            return TriState('Ø')

    def to_binary(self):
        return {'0': 0, '1': 1, 'Ø': 0.5}[self.state]

    def color(self):
        return {'0': 'black', '1': 'white', 'Ø': 'purple'}[self.state]

    def narrate(self):
        return {
            '0': "Void detected. Awaiting signal.",
            '1': "Signal active. Assimilation underway.",
            'Ø': "Fusion achieved. Mutation lineage updated."
        }[self.state]

# ─────────────────────────────────────────────────────────────
# Live System Data Feed
# ─────────────────────────────────────────────────────────────
def get_system_state():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    entropy = (cpu + mem) / 200
    if entropy < 0.33:
        return TriState('0')
    elif entropy < 0.66:
        return TriState('1')
    else:
        return TriState('Ø')

def get_secondary_state():
    threads = threading.active_count()
    if threads < 10:
        return TriState('0')
    elif threads < 50:
        return TriState('1')
    else:
        return TriState('Ø')

# ─────────────────────────────────────────────────────────────
# Cognitive Rune Mapping
# ─────────────────────────────────────────────────────────────
def get_cognitive_rune(entropy):
    if entropy < 0.33:
        return 'Ψ'  # Focused void
    elif entropy < 0.66:
        return 'Δ'  # Active signal
    else:
        return '∞'  # Fusion achieved

# ─────────────────────────────────────────────────────────────
# Zero-Trust Purge Logic
# ─────────────────────────────────────────────────────────────
def purge_sensitive_data():
    try:
        path = "borg_temp.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("█" * 1024)
        os.remove(path)
    except Exception as e:
        print(f"[Purge Error] {e}")

# ─────────────────────────────────────────────────────────────
# Symbolic Memory Pattern (Real-Time)
# ─────────────────────────────────────────────────────────────
def generate_memory_pattern():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    entropy = (mem.percent + swap.percent) / 200
    states = []
    for _ in range(8):
        if entropy < 0.33:
            states.append('0')
        elif entropy < 0.66:
            states.append('1')
        else:
            states.append('Ø')
    return states

def render_memory_pattern(canvas, pattern):
    x_start = 100
    y = 620
    for i, state in enumerate(pattern):
        color = {'0': 'black', '1': 'white', 'Ø': 'purple'}[state]
        canvas.create_rectangle(x_start + i*60, y, x_start + i*60 + 50, y + 50, fill=color, outline='gray')
        canvas.create_text(x_start + i*60 + 25, y + 65, text=state, fill='lightgray', font=('Consolas', 10))

# ─────────────────────────────────────────────────────────────
# Swarm Sync Scaffold
# ─────────────────────────────────────────────────────────────
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

# ─────────────────────────────────────────────────────────────
# GUI Shell
# ─────────────────────────────────────────────────────────────
class BorgAssimilationGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=700, bg='gray10')
        self.canvas.pack()
        self.history = []
        self.memory_pattern = generate_memory_pattern()
        self.run_loop()

    def run_loop(self):
        def loop():
            while True:
                a = get_system_state()
                b = get_secondary_state()
                fusion = a.mutate(b)

                self.history.append((a, b, fusion))
                if len(self.history) > 12:
                    self.history.pop(0)

                if fusion.state == 'Ø':
                    purge_sensitive_data()

                self.memory_pattern = generate_memory_pattern()
                self.render(a, b, fusion)
        threading.Thread(target=loop, daemon=True).start()

    def render(self, a, b, fusion):
        self.canvas.delete("all")

        # Nodes
        self.canvas.create_oval(100, 100, 200, 200, fill=a.color(), outline='cyan', width=2)
        self.canvas.create_text(150, 220, text=f"A: {a.state}", fill='cyan', font=('Consolas', 12))
        self.canvas.create_text(150, 240, text=a.narrate(), fill='lightblue', font=('Consolas', 9))

        self.canvas.create_oval(600, 100, 700, 200, fill=b.color(), outline='magenta', width=2)
        self.canvas.create_text(650, 220, text=f"B: {b.state}", fill='magenta', font=('Consolas', 12))
        self.canvas.create_text(650, 240, text=b.narrate(), fill='pink', font=('Consolas', 9))

        self.canvas.create_oval(350, 350, 450, 450, fill=fusion.color(), outline='yellow', width=3)
        self.canvas.create_text(400, 470, text=f"Fusion: {fusion.state}", fill='yellow', font=('Consolas', 14, 'bold'))
        self.canvas.create_text(400, 490, text=fusion.narrate(), fill='gold', font=('Consolas', 10))

        # Cognitive Rune
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        entropy = (cpu + mem) / 200
        rune = get_cognitive_rune(entropy)
        self.canvas.create_text(400, 515, text=f"Cognitive Rune: {rune}", fill='cyan', font=('Consolas', 18, 'bold'))

        # Mutation History
        y = 20
        self.canvas.create_text(400, y, text="Mutation Lineage", fill='white', font=('Consolas', 12, 'underline'))
        for i, (s1, s2, f) in enumerate(reversed(self.history)):
            y += 20
            lineage = f"{s1.state} + {s2.state} → {f.state}"
            self.canvas.create_text(400, y, text=lineage, fill='lightgray', font=('Consolas', 10))

        # Symbolic Memory Pattern
        self.canvas.create_text(400, 590, text="Symbolic Memory Pattern", fill='lightgreen', font=('Consolas', 12, 'underline'))
        render_memory_pattern(self.canvas, self.memory_pattern)

        # Swarm Node
        ip = get_local_ip()
        self.canvas.create_text(400, 660, text=f"Swarm Node: {ip}", fill='orange', font=('Consolas', 10, 'italic'))

# ─────────────────────────────────────────────────────────────
# Launch Shell
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Operation: Borg Assimilation — Real-Time Symbolic Shell")
    root.geometry("800x700")
    app = BorgAssimilationGUI(root)
    root.mainloop()
