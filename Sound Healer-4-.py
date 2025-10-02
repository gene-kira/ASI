import numpy as np, sounddevice as sd, socket, threading, time, tkinter as tk
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class MagicBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MagicBox Sonic Healer : Swarm Synced")
        self.geometry("1100x750")
        self.configure(bg="#1e1e2f")

        self.freqs = {
            "174 Hz – Pain Relief": 174, "396 Hz – Release Fear": 396,
            "528 Hz – DNA Repair": 528, "639 Hz – Relationship Healing": 639,
            "741 Hz – Problem Solving": 741, "852 Hz – Intuition Activation": 852
        }

        self.sample_rate, self.node, self.port = 44100, socket.gethostname(), 6666
        self.running, self.wave = False, np.zeros(44100)

        # Top Controls
        top = tk.Frame(self, bg="#1e1e2f"); top.pack(pady=5)
        self.freq_box = ttk.Combobox(top, values=list(self.freqs.keys()), state="readonly", width=30)
        self.freq_box.set("528 Hz – DNA Repair"); self.freq_box.grid(row=0, column=0, padx=5)
        self.slider = ttk.Scale(top, from_=10, to=300, orient="horizontal", command=self.update_duration)
        self.slider.set(70); self.slider.grid(row=0, column=1, padx=5)
        self.duration_label = ttk.Label(top, text="70 mins", background="#1e1e2f", foreground="white")
        self.duration_label.grid(row=0, column=2, padx=5)

        # Narration
        self.narration = ttk.Label(self, text="↔ Cosmic lattice resonating…", background="#1e1e2f", foreground="white")
        self.narration.pack()

        # Plots
        fig = Figure(figsize=(9, 3), dpi=100)
        self.ax1, self.ax2 = fig.add_subplot(121), fig.add_subplot(122)
        canvas = FigureCanvasTkAgg(fig, master=self); canvas.get_tk_widget().pack()

        # Biometric + Rituals
        ttk.Label(self, text="Heart Rate: 62 BPM | EEG Delta: 6.5 Hz", foreground="lime", background="#1e1e2f").pack()
        rituals = tk.Frame(self, bg="#1e1e2f"); rituals.pack()
        for txt, cmd in [("↻ Memory Overlay", self.overlay), ("⚡ Polarity Reset", self.reset), ("🌌 Cosmic Connection", self.sync)]:
            ttk.Button(rituals, text=txt, command=cmd).pack(side="left", padx=10)

        # Log + Controls
        self.log = scrolledtext.ScrolledText(self, height=8, bg="#2e2e3f", fg="white", font=("Consolas", 10))
        self.log.pack(fill="x", padx=10)
        controls = tk.Frame(self, bg="#1e1e2f"); controls.pack(pady=10)
        ttk.Button(controls, text="Activate Healing Sequence", command=self.play).pack(side="left", padx=10)
        ttk.Button(controls, text="■ Stop", command=self.stop, style="TButton").pack(side="left", padx=10)

        threading.Thread(target=self.listen, daemon=True).start()

    def update_duration(self, val): self.duration_label.config(text=f"{int(float(val))} mins")

    def play(self):
        label = self.freq_box.get(); freq = self.freqs[label]
        dur = int(float(self.slider.get())) * 60
        self.narration.config(text=f"🔮 {label} – Resonance field expanding…")
        self.log_msg(f"[Launch] {label} session initialized")
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        self.wave = np.sin(2 * np.pi * freq * t)
        sd.play(self.wave, self.sample_rate)
        self.running = True
        self.plot(freq)
        self.broadcast(f"[{self.node}] Healing: {label}")
        self.log_msg(f"[Active] {label} ({dur//60} mins)")

    def stop(self):
        sd.stop(); self.running = False
        self.narration.config(text="⛔ Healing sequence stopped.")
        self.log_msg("[Stopped] Playback halted.")

    def plot(self, freq):
        self.ax1.clear(); self.ax1.plot(self.wave[:1000], color='cyan')
        self.ax1.set_title("Sequence"); self.ax1.grid(True)
        fft = np.abs(np.fft.rfft(self.wave[:10000]))
        freqs = np.fft.rfftfreq(len(self.wave[:10000]), 1 / self.sample_rate)
        self.ax2.clear(); self.ax2.plot(freqs, fft, color='purple')
        self.ax2.set_title("Frequency Spec↔trum"); self.ax2.grid(True)
        self.ax1.set_ylim(-1, 1); self.ax2.set_ylim(0, 0.5)
        self.ax2.set_xlim(0, 3000)
        self.ax2.set_xlabel("Frequency (Hz)")
        self.ax1.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Amplitude")

    def broadcast(self, msg):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(msg.encode(), ('<broadcast>', self.port))
            self.log_msg(f"[Connected] {msg}")
        except Exception as e:
            self.log_msg(f"[ERROR] Broadcast failed: {e}")

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.port))
        while True:
            msg = sock.recv(1024).decode()
            self.log_msg(f"[Swarm] {msg}")

    def overlay(self): self.narration.config(text="🧠 Memory lattice realigned."); self.log_msg("[Ritual] Memory overlay")
    def reset(self): self.narration.config(text="⚡ Polarity field neutralized."); self.log_msg("[Ritual] Polarity reset")
    def sync(self): self.narration.config(text="🌌 Cosmic lattice synchronized."); self.log_msg("[Ritual] Cosmic connection")

    def log_msg(self, msg):
        self.log.insert(tk.END, f"{time.strftime('%H:%M')} {msg}\n")
        self.log.see(tk.END)

if __name__ == "__main__":
    MagicBox().mainloop()

