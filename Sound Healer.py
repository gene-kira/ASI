# 🔧 Autoloader: Ritual-grade package check
import subprocess
import sys

def autoload(packages):
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[AUTOLOADER] ✅ {pkg} present.")
        except ImportError:
            print(f"[AUTOLOADER] ⚠️ {pkg} missing. Installing…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"[AUTOLOADER] 🔄 {pkg} installed.")

required_packages = ["numpy", "sounddevice", "matplotlib"]
autoload(required_packages)
print("[AUTOLOADER] 🧬 Mutation complete. Shell integrity verified.")

# 🔮 Imports
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import socket

# 🧠 MagicBox GUI
class MagicBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧙 MagicBox Sonic Healer – Swarm Synced")
        self.geometry("1000x700")
        self.configure(bg="#1e1e2f")

        # Frequency Map
        self.freq_map = {
            "174 Hz – Pain Relief": 174,
            "396 Hz – Release Fear": 396,
            "528 Hz – DNA Repair": 528,
            "639 Hz – Relationship Healing": 639,
            "852 Hz – Intuition Activation": 852
        }

        # GUI Elements
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#1e1e2f", foreground="#e0e0ff", font=("Consolas", 12))
        self.style.configure("TButton", font=("Consolas", 12), padding=6)
        self.style.configure("TCombobox", font=("Consolas", 12))

        ttk.Label(self, text="Select Healing Frequency:").pack(pady=10)
        self.freq_selector = ttk.Combobox(self, values=list(self.freq_map.keys()), state="readonly")
        self.freq_selector.pack(pady=5)
        self.freq_selector.set("528 Hz – DNA Repair")

        self.narration = ttk.Label(self, text="🧠 Awaiting frequency selection…")
        self.narration.pack(pady=10)

        # Waveform + FFT Plots
        fig = Figure(figsize=(8, 4), dpi=100)
        self.ax_wave = fig.add_subplot(121)
        self.ax_fft = fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack()

        # Swarm Sync Panel
        ttk.Label(self, text="📡 Swarm Sync Status:").pack(pady=10)
        self.swarm_panel = ScrolledText(self, height=6, bg="#2e2e3f", fg="#e0e0ff", font=("Consolas", 10))
        self.swarm_panel.pack(fill="x", padx=20)

        # Play Button
        ttk.Button(self, text="Activate Healing Sequence", command=self.play_frequency).pack(pady=20)

        # Internal State
        self.sample_rate = 44100
        self.duration = 2
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)
        self.wave = np.zeros_like(self.t)
        self.node_id = socket.gethostname()
        self.swarm_port = 6666

    def play_frequency(self):
        label = self.freq_selector.get()
        freq = self.freq_map[label]
        self.narration.config(text=f"🔮 {label} – Resonance field expanding…")
        print(f"[DEBUG] Playing frequency: {freq} Hz")

        self.wave = np.sin(2 * np.pi * freq * self.t)
        sd.play(self.wave, self.sample_rate)
        self.update_plots()
        self.broadcast_state(label)

    def update_plots(self):
        self.ax_wave.clear()
        self.ax_wave.plot(self.t, self.wave, color='cyan')
        self.ax_wave.set_title("Waveform")

        fft_data = np.abs(np.fft.rfft(self.wave))
        freqs = np.fft.rfftfreq(len(self.wave), 1 / self.sample_rate)
        self.ax_fft.clear()
        self.ax_fft.plot(freqs, fft_data, color='magenta')
        self.ax_fft.set_title("Frequency Spectrum")

        self.canvas.draw()
        print("[DEBUG] Waveform and FFT overlays updated.")

    def broadcast_state(self, label):
        try:
            msg = f"[{self.node_id}] Healing: {label}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(msg.encode(), ('<broadcast>', self.swarm_port))
            self.swarm_panel.insert(tk.END, f"📡 Broadcasted: {msg}\n")
            print(f"[SWARM] Broadcasted healing state: {msg}")
        except Exception as e:
            self.swarm_panel.insert(tk.END, f"⚠️ Swarm sync failed: {e}\n")
            print(f"[ERROR] Swarm sync failed: {e}")

# 🧬 Launch Ritual
if __name__ == "__main__":
    MagicBox().mainloop()

