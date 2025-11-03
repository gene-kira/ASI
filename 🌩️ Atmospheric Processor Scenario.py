import tkinter as tk
import threading
import random
import time

# Energy calculation function
def calculate_energy(strikes, voltage, current, duration, efficiency):
    return strikes * voltage * current * duration * efficiency

# Daemon thread to simulate lightning strikes
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

# GUI overlay
class StormHarvestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Storm Harvest Overlay")
        self.root.geometry("500x300")
        self.root.configure(bg="black")

        self.strike_label = tk.Label(root, text="Strikes: 0", fg="cyan", bg="black", font=("Consolas", 16))
        self.strike_label.pack(pady=10)

        self.energy_label = tk.Label(root, text="Energy: 0 J", fg="lime", bg="black", font=("Consolas", 16))
        self.energy_label.pack(pady=10)

        self.canvas = tk.Canvas(root, width=480, height=150, bg="black", highlightthickness=0)
        self.canvas.pack()

    def update_overlay(self, strikes, energy):
        self.strike_label.config(text=f"Strikes: {strikes}")
        self.energy_label.config(text=f"Energy: {energy:.2e} J")
        self.canvas.delete("all")
        for _ in range(strikes):
            x = random.randint(0, 480)
            self.canvas.create_line(x, 0, x, 150, fill="yellow", width=2)

# Launch GUI and daemon
def launch_storm_harvest():
    root = tk.Tk()
    gui = StormHarvestGUI(root)
    daemon = LightningCaptureDaemon(gui.update_overlay)
    daemon.start()
    root.mainloop()

launch_storm_harvest()

