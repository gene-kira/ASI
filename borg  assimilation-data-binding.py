import tkinter as tk
import random
import psutil
import threading
import time

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
# GUI Shell
# ─────────────────────────────────────────────────────────────
class ThoughtPatternGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=600, bg='gray20')
        self.canvas.pack()
        self.history = []
        self.run_loop()

    def run_loop(self):
        def loop():
            while True:
                a = get_system_state()
                b = TriState(random.choice(['0', '1', 'Ø']))
                fusion = a.mutate(b)

                self.history.append((a.state, b.state, fusion.state))
                if len(self.history) > 10:
                    self.history.pop(0)

                self.render(a, b, fusion)
                time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    def render(self, a, b, fusion):
        self.canvas.delete("all")

        # Nodes
        self.canvas.create_oval(100, 100, 200, 200, fill=a.color(), outline='cyan', width=2)
        self.canvas.create_text(150, 220, text=f"A: {a.state}", fill='cyan', font=('Consolas', 12))

        self.canvas.create_oval(400, 100, 500, 200, fill=b.color(), outline='magenta', width=2)
        self.canvas.create_text(450, 220, text=f"B: {b.state}", fill='magenta', font=('Consolas', 12))

        self.canvas.create_oval(250, 350, 350, 450, fill=fusion.color(), outline='yellow', width=3)
        self.canvas.create_text(300, 470, text=f"Fusion: {fusion.state}", fill='yellow', font=('Consolas', 14, 'bold'))

        # Mutation History
        y = 20
        self.canvas.create_text(300, y, text="Mutation Lineage", fill='white', font=('Consolas', 12, 'underline'))
        for i, (s1, s2, f) in enumerate(reversed(self.history)):
            y += 20
            self.canvas.create_text(300, y, text=f"{s1} + {s2} → {f}", fill='lightgray', font=('Consolas', 10))

# ─────────────────────────────────────────────────────────────
# Launch Shell
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Symbolic Thought Shell — Tri-State Mutation Engine")
    root.geometry("600x600")
    app = ThoughtPatternGUI(root)
    root.mainloop()

