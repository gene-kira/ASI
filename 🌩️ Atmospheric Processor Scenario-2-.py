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
        self.root.geometry("800x600")
        self.root.configure(bg="black")

        # Strike Monitor Panel
        self.strike_frame = tk.Frame(root, bg="black")
        self.strike_frame.pack(pady=10)
        self.strike_label = tk.Label(self.strike_frame, text="⚡ Strikes: 0", fg="cyan", bg="black", font=("Consolas", 18))
        self.strike_label.pack()

        # Energy Glyph Panel
        self.energy_label = tk.Label(root, text="🔋 Energy: 0 J", fg="lime", bg="black", font=("Consolas", 18))
        self.energy_label.pack(pady=10)

        # Cloud Charge Map
        self.canvas = tk.Canvas(root, width=760, height=300, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Daemon Sync Status
        self.sync_label = tk.Label(root, text="🌀 Sync Status: Stable", fg="magenta", bg="black", font=("Consolas", 16))
        self.sync_label.pack(pady=10)

        # Resurrection Detection
        self.res_label = tk.Label(root, text="☠ Resurrection Glyphs: None", fg="red", bg="black", font=("Consolas", 16))
        self.res_label.pack(pady=10)

    def update_overlay(self, strikes, energy):
        self.strike_label.config(text=f"⚡ Strikes: {strikes}")
        self.energy_label.config(text=f"🔋 Energy: {energy:.2e} J")

        # Update canvas with lightning arcs
        self.canvas.delete("all")
        for _ in range(strikes):
            x = random.randint(0, 760)
            self.canvas.create_line(x, 0, x, 300, fill="yellow", width=2)

        # Sync status logic
        if energy > 1e11:
            self.sync_label.config(text="🌀 Sync Status: Overloaded", fg="orange")
            self.res_label.config(text="☠ Resurrection Glyphs: Activated", fg="red")
        else:
            self.sync_label.config(text="🌀 Sync Status: Stable", fg="magenta")
            self.res_label.config(text="☠ Resurrection Glyphs: None", fg="red")

# Launch GUI
def launch_storm_harvest():
    root = tk.Tk()
    gui = StormHarvestOverlay(root)
    daemon = LightningCaptureDaemon(gui.update_overlay)
    daemon.start()
    root.mainloop()

launch_storm_harvest()

