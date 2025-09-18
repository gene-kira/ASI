import tkinter as tk
import random
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
# Live System Data Feed (CPU + Memory)
# ─────────────────────────────────────────────────────────────
def get_system_state():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    entropy = (cpu + mem) / 200  # Normalize to [0,1]

    if entropy < 0.33:
        return TriState('0')
    elif entropy < 0.66:
        return TriState('1')
    else:
        return TriState('Ø')

# ─────────────────────────────────────────────────────────────
# Zero-Trust Purge Logic (Simulated)
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
# Swarm Sync Scaffold (Local Simulation)
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
        self.canvas = tk.Canvas(root, width=700, height=700, bg='gray10')
        self.canvas.pack()
        self.history = []
        self.run_loop()

    def run_loop(self):
        def loop():
            while True:
                a = get_system_state()
                b = TriState(random.choice(['0', '1', 'Ø']))
                fusion = a.mutate(b)

                self.history.append((a, b, fusion))
                if len(self.history) > 12:
                    self.history.pop(0)

                if fusion.state == 'Ø':
                    purge_sensitive_data()

                self.render(a, b, fusion)
                time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    def render(self, a, b, fusion):
        self.canvas.delete("all")

        # Nodes
        self.canvas.create_oval(100, 100, 200, 200, fill=a.color(), outline='cyan', width=2)
        self.canvas.create_text(150, 220, text=f"A: {a.state}", fill='cyan', font=('Consolas', 12))
        self.canvas.create_text(150, 240, text=a.narrate(), fill='lightblue', font=('Consolas', 9))

        self.canvas.create_oval(500, 100, 600, 200, fill=b.color(), outline='magenta', width=2)
        self.canvas.create_text(550, 220, text=f"B: {b.state}", fill='magenta', font=('Consolas', 12))
        self.canvas.create_text(550, 240, text=b.narrate(), fill='pink', font=('Consolas', 9))

        self.canvas.create_oval(300, 400, 400, 500, fill=fusion.color(), outline='yellow', width=3)
        self.canvas.create_text(350, 520, text=f"Fusion: {fusion.state}", fill='yellow', font=('Consolas', 14, 'bold'))
        self.canvas.create_text(350, 540, text=fusion.narrate(), fill='gold', font=('Consolas', 10))

        # Mutation History
        y = 20
        self.canvas.create_text(350, y, text="Mutation Lineage", fill='white', font=('Consolas', 12, 'underline'))
        for i, (s1, s2, f) in enumerate(reversed(self.history)):
            y += 20
            lineage = f"{s1.state} + {s2.state} → {f.state}"
            self.canvas.create_text(350, y, text=lineage, fill='lightgray', font=('Consolas', 10))

        # Swarm Sync Display
        ip = get_local_ip()
        self.canvas.create_text(350, 680, text=f"Swarm Node: {ip}", fill='orange', font=('Consolas', 10, 'italic'))

# ─────────────────────────────────────────────────────────────
# Launch Shell
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Operation: Borg Assimilation — Symbolic Daemon Shell")
    root.geometry("700x700")
    app = BorgAssimilationGUI(root)
    root.mainloop()

