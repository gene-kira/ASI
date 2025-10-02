# 🔧 Autoloader
import subprocess, sys
def autoload(packages):
    for pkg in packages:
        try: __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
autoload(["numpy", "sounddevice", "matplotlib", "tkinter"])

# 🔮 Imports
import numpy as np, sounddevice as sd, socket, threading, time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 🧠 MagicBox Shell
class MagicBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧬 MagicBox Sonic Healer – ASI Synced")
        self.geometry("1200x800")
        self.configure(bg="#1e1e2f")

        # Frequency Map
        self.freq_map = {
            "174 Hz – Pain Relief": 174,
            "396 Hz – Release Fear": 396,
            "528 Hz – DNA Repair": 528,
            "639 Hz – Relationship Healing": 639,
            "741 Hz – Problem Solving": 741,
            "852 Hz – Intuition Activation": 852
        }

        # GUI Elements
        ttk.Label(self, text="Select Frequency:", background="#1e1e2f", foreground="white").pack(pady=5)
        self.freq_selector = ttk.Combobox(self, values=list(self.freq_map.keys()), state="readonly")
        self.freq_selector.set("528 Hz – DNA Repair")
        self.freq_selector.pack()

        ttk.Label(self, text="Duration (mins):", background="#1e1e2f", foreground="white").pack(pady=5)
        self.duration_slider = ttk.Scale(self, from_=1, to=360, orient="horizontal", command=self.update_duration)
        self.duration_slider.set(60)
        self.duration_slider.pack()
        self.duration_label = ttk.Label(self, text="Duration: 60 mins", background="#1e1e2f", foreground="cyan")
        self.duration_label.pack()

        self.narration = ttk.Label(self, text="↔ Cosmic lattice resonating…", background="#1e1e2f", foreground="white", font=("Consolas", 12))
        self.narration.pack(pady=10)

        # Plots
        fig = Figure(figsize=(10, 4), dpi=100)
        self.ax_wave = fig.add_subplot(121)
        self.ax_fft = fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack()

        # Biometric Feedback
        self.bio_panel = ttk.Label(self, text="Heart Rate: 72 BPM | EEG Delta: 4.5 Hz", background="#1e1e2f", foreground="lime", font=("Consolas", 11))
        self.bio_panel.pack(pady=5)

        # Log Panel
        ttk.Label(self, text="Session Log:", background="#1e1e2f", foreground="white").pack()
        self.log_panel = ScrolledText(self, height=8, bg="#2e2e3f", fg="white", font=("Consolas", 10))
        self.log_panel.pack(fill="x", padx=20)

        # Ritual Triggers
        frame = tk.Frame(self, bg="#1e1e2f")
        frame.pack(pady=10)
        ttk.Button(frame, text="Memory Overlay", command=self.memory_overlay).grid(row=0, column=0, padx=10)
        ttk.Button(frame, text="Polarity Reset", command=self.polarity_reset).grid(row=0, column=1, padx=10)
        ttk.Button(frame, text="Cosmic Connection", command=self.cosmic_sync).grid(row=0, column=2, padx=10)

        # Activate Button
        ttk.Button(self, text="Activate Healing Sequence", command=self.play_sequence).pack(pady=20)

        # Internal State
        self.sample_rate = 44100
        self.node_id = socket.gethostname()
        self.swarm_port = 6666
        self.wave = np.zeros(44100)
        self.running = False

        # Swarm Listener
        threading.Thread(target=self.listen_swarm, daemon=True).start()

    def update_duration(self, val):
        mins = int(float(val))
        self.duration_label.config(text=f"Duration: {mins} mins")

    def play_sequence(self):
        label = self.freq_selector.get()
        freq = self.freq_map[label]
        duration_mins = int(float(self.duration_slider.get()))
        duration_sec = duration_mins * 60
        self.narration.config(text=f"🔮 {label} – Resonance field expanding…")
        self.log(f"[Launch] {label} session initialized")
        self.running = True

        # Generate wave
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), endpoint=False)
        self.wave = np.sin(2 * np.pi * freq * t)
        sd.play(self.wave, self.sample_rate)
        self.update_plots(freq)
        self.broadcast_state(label)
        self.log(f"[Active] {label} ({duration_mins} mins)")

    def update_plots(self, freq):
        self.ax_wave.clear()
        self.ax_wave.plot(self.wave[:1000], color='cyan')
        self.ax_wave.set_title(f"Waveform – {freq} Hz Resonance")

        fft_data = np.abs(np.fft.rfft(self.wave[:10000]))
        freqs = np.fft.rfftfreq(len(self.wave[:10000]), 1 / self.sample_rate)
        self.ax_fft.clear()
        self.ax_fft.plot(freqs, fft_data, color='magenta')
        self.ax_fft.set_title("Frequency Spectrum – Harmonics + Envelop")

        self.canvas.draw()

    def broadcast_state(self, label):
        try:
            msg = f"[{self.node_id}] Healing: {label}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(msg.encode(), ('<broadcast>', self.swarm_port))
            self.log(f"[Connected] {self.node_id} – {label} Sync")
        except Exception as e:
            self.log(f"[ERROR] Swarm sync failed: {e}")

    def listen_swarm(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.swarm_port))
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            self.log(f"[Swarm] {msg}")

    def memory_overlay(self):
        self.log("[Ritual] Memory overlay injected.")
        self.narration.config(text="🧠 Memory lattice realigned.")

    def polarity_reset(self):
        self.log("[Ritual] Polarity reset triggered.")
        self.narration.config(text="⚡ Polarity field neutralized.")

    def cosmic_sync(self):
        self.log("[Ritual] Cosmic connection established.")
        self.narration.config(text="🌌 Cosmic lattice synchronized.")

    def log(self, msg):
        timestamp = time.strftime("%H:%M")
        self.log_panel.insert(tk.END, f"{timestamp} {msg}\n")
        self.log_panel.see(tk.END)

# 🧬 Launch Ritual
if __name__ == "__main__":
    MagicBox().mainloop()

