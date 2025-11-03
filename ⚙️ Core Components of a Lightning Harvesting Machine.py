import tkinter as tk
import threading
import random
import time

def calculate_energy(strikes, voltage, current, duration, efficiency):
    return strikes * voltage * current * duration * efficiency

class StormHarvestPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Codex Purge Shell – Storm Harvest Panel")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")

        # Strike Capture Panel
        self.strike_canvas = tk.Canvas(root, width=960, height=150, bg="black", highlightthickness=0)
        self.strike_canvas.pack(pady=10)
        self.strike_label = tk.Label(root, text="⚡ Strikes: 0", fg="yellow", bg="black", font=("Consolas", 16))
        self.strike_label.pack()

        # Energy Routing Panel
        self.energy_canvas = tk.Canvas(root, width=960, height=150, bg="black", highlightthickness=0)
        self.energy_canvas.pack(pady=10)
        self.energy_label = tk.Label(root, text="🔋 Energy: 0 J", fg="lime", bg="black", font=("Consolas", 16))
        self.energy_label.pack()

        # Sync Feedback Panel
        self.sync_canvas = tk.Canvas(root, width=960, height=150, bg="black", highlightthickness=0)
        self.sync_canvas.pack(pady=10)
        self.sync_label = tk.Label(root, text="🌀 Sync Status: Stable", fg="cyan", bg="black", font=("Consolas", 16))
        self.sync_label.pack()

    def update(self, strikes, energy, sync):
        # Strike Capture
        self.strike_label.config(text=f"⚡ Strikes: {strikes}")
        self.strike_canvas.delete("all")
        for _ in range(strikes):
            x = random.randint(0, 960)
            self.strike_canvas.create_line(x, 0, x, 150, fill="yellow", width=2)

        # Energy Routing
        self.energy_label.config(text=f"🔋 Energy: {energy:.2e} J")
        self.energy_canvas.delete("all")
        bar_length = min(int(energy / 1e9), 960)
        self.energy_canvas.create_rectangle(0, 130, bar_length, 150, fill="lime")

        # Sync Feedback
        self.sync_canvas.delete("all")
        if sync < 50:
            self.sync_label.config(text="🌀 Sync Status: Desynced", fg="red")
            self.sync_canvas.create_text(480, 75, text="⚠ Node Misalignment", fill="red", font=("Consolas", 18))
        elif sync < 80:
            self.sync_label.config(text="🌀 Sync Status: Partial", fg="orange")
            self.sync_canvas.create_text(480, 75, text="⧗ Sync Stabilizing", fill="orange", font=("Consolas", 18))
        else:
            self.sync_label.config(text="🌀 Sync Status: Stable", fg="cyan")
            self.sync_canvas.create_text(480, 75, text="✔ Nodes Aligned", fill="cyan", font=("Consolas", 18))

class StormDaemon(threading.Thread):
    def __init__(self, gui_callback):
        super().__init__(daemon=True)
        self.gui_callback = gui_callback

    def run(self):
        while True:
            strikes = random.randint(1, 5)
            energy = calculate_energy(strikes, 1e9, 30000, 0.0002, 0.75)
            sync = random.randint(30, 100)
            self.gui_callback(strikes, energy, sync)
            time.sleep(2)

def launch_gui():
    root = tk.Tk()
    panel = StormHarvestPanel(root)
    daemon = StormDaemon(panel.update)
    daemon.start()
    root.mainloop()

launch_gui()

