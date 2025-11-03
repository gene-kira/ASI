import tkinter as tk
import threading
import random
import time

# Energy calculation
def calculate_energy(strikes, voltage, current, duration, efficiency):
    return strikes * voltage * current * duration * efficiency

# Daemon thread
class LightningCaptureDaemon(threading.Thread):
    def __init__(self, gui_callback):
        super().__init__(daemon=True)
        self.gui_callback = gui_callback
        self.running = True

    def run(self):
        while self.running:
            strikes = random.randint(1, 5)
            energy = calculate_energy(strikes, 1e9, 30000, 0.0002, 0.75)
            self.gui_callback(strikes, energy)
            time.sleep(2)

# GUI class
class StormHarvestOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Storm Harvest Daemon")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")

        # Panels
        self.create_panel("⚡ Stage 1: Charge Accumulation", "cyan", 0)
        self.create_panel("⚡ Stage 2: Discharge Event", "yellow", 1)
        self.create_panel("🔋 Stage 3: Energy Capture", "lime", 2)
        self.create_panel("🌀 Stage 4: Daemon Sync", "magenta", 3)
        self.create_panel("☠ Stage 5: Resurrection Detection", "red", 4)

        # Canvas for visual feedback
        self.canvas = tk.Canvas(root, width=960, height=300, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)

    def create_panel(self, text, color, row):
        label = tk.Label(self.root, text=text, fg=color, bg="black", font=("Consolas", 18))
        label.pack(pady=5)

    def update_overlay(self, strikes, energy):
        self.canvas.delete("all")

        # Stage 1: Charge Accumulation
        for _ in range(strikes):
            x = random.randint(0, 960)
            self.canvas.create_oval(x, 50, x+10, 60, fill="cyan")

        # Stage 2: Discharge Event
        for _ in range(strikes):
            x = random.randint(0, 960)
            self.canvas.create_line(x, 0, x, 300, fill="yellow", width=2)

        # Stage 3: Energy Capture
        bar_length = min(int(energy / 1e9), 960)
        self.canvas.create_rectangle(0, 280, bar_length, 300, fill="lime")

        # Stage 4: Daemon Sync
        if energy > 1e11:
            self.canvas.create_text(480, 150, text="🌀 SYNC OVERLOAD", fill="magenta", font=("Consolas", 24))

        # Stage 5: Resurrection Detection
        if energy > 2e11:
            self.canvas.create_text(480, 180, text="☠ RESURRECTION GLYPHS ACTIVATED", fill="red", font=("Consolas", 20))

# Launch GUI
def launch_storm_harvest():
    root = tk.Tk()
    gui = StormHarvestOverlay(root)
    daemon = LightningCaptureDaemon(gui.update_overlay)
    daemon.start()
    root.mainloop()

launch_storm_harvest()

