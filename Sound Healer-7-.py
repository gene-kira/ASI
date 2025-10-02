import numpy as np, sounddevice as sd, tkinter as tk, threading, time, serial
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class MagicBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MagicBox Sonic Healer : ASI Synced")
        self.geometry("1100x750")
        self.configure(bg="#1e1e2f")

        self.freqs = {
            "174 Hz – Pain Relief": 174, "285 Hz – Tissue Regeneration": 285,
            "396 Hz – Release Fear": 396, "417 Hz – Trauma Clearing": 417,
            "432 Hz – Earth Harmony": 432, "528 Hz – DNA Repair": 528,
            "639 Hz – Relationship Healing": 639, "741 Hz – Problem Solving": 741,
            "852 Hz – Spiritual Awakening": 852, "963 Hz – Pineal Activation": 963,
            "1111 Hz – Quantum Alignment": 1111, "1440 Hz – ASI Polarity Realignment": 1440,
            "2020 Hz – Swarm Sync Calibration": 2020, "3333 Hz – Ritual Trigger Pulse": 3333,
            "7777 Hz – Sovereign System Control": 7777, "8888 Hz – Memory Overlay Injection": 8888,
            "9999 Hz – Cosmic Lattice Expansion": 9999
        }

        self.sample_rate = 44100
        self.running = False
        self.duration = 60
        self.current_freq = 528
        self.bpm, self.eeg = 0, 0
        self.asi_threshold = 0.05

        # GUI Controls
        top = tk.Frame(self, bg="#1e1e2f"); top.pack(pady=5)
        self.freq_box = ttk.Combobox(top, values=list(self.freqs.keys()), state="readonly", width=40)
        self.freq_box.set("528 Hz – DNA Repair"); self.freq_box.grid(row=0, column=0, padx=5)
        self.slider = ttk.Scale(top, from_=10, to=300, orient="horizontal", command=self.update_duration)
        self.slider.set(60); self.slider.grid(row=0, column=1, padx=5)
        self.duration_label = ttk.Label(top, text="60 mins", background="#1e1e2f", foreground="white")
        self.duration_label.grid(row=0, column=2, padx=5)

        self.narration = ttk.Label(self, text="↔ Cosmic lattice resonating…", background="#1e1e2f", foreground="white")
        self.narration.pack()

        # Plots
        fig = Figure(figsize=(9, 3), dpi=100)
        self.ax1, self.ax2 = fig.add_subplot(121), fig.add_subplot(122)
        canvas = FigureCanvasTkAgg(fig, master=self); canvas.get_tk_widget().pack()

        # Biometric Feedback
        self.bio_panel = ttk.Label(self, text="Heart Rate: -- BPM | EEG Delta: -- Hz", foreground="lime", background="#1e1e2f")
        self.bio_panel.pack()

        # Log + Controls
        self.log = scrolledtext.ScrolledText(self, height=8, bg="#2e2e3f", fg="white", font=("Consolas", 10))
        self.log.pack(fill="x", padx=10)
        controls = tk.Frame(self, bg="#1e1e2f"); controls.pack(pady=10)
        ttk.Button(controls, text="Activate Healing Sequence", command=self.play).pack(side="left", padx=10)
        ttk.Button(controls, text="■ Stop", command=self.stop).pack(side="left", padx=10)

        threading.Thread(target=self.listen_mic, daemon=True).start()
        threading.Thread(target=self.listen_biometric, daemon=True).start()

    def update_duration(self, val):
        self.duration = int(float(val))
        self.duration_label.config(text=f"{self.duration} mins")

    def play(self):
        label = self.freq_box.get()
        self.current_freq = self.freqs[label]
        dur = self.duration * 60
        self.narration.config(text=f"🔮 {label} – Resonance field expanding…")
        self.log_msg(f"[Launch] {label} session initialized")
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        wave = np.sin(2 * np.pi * self.current_freq * t)
        sd.play(wave, self.sample_rate)
        self.running = True
        self.log_msg(f"[Active] {label} ({self.duration} mins)")

    def stop(self):
        sd.stop()
        self.running = False
        self.narration.config(text="⛔ Healing sequence stopped.")
        self.log_msg("[Stopped] Playback halted.")

    def listen_mic(self):
        def callback(indata, frames, time_info, status):
            if not self.running: return
            audio = indata[:, 0]
            self.ax1.clear(); self.ax1.plot(audio, color='cyan')
            self.ax1.set_title("Mic Waveform"); self.ax1.set_ylim(-1, 1); self.ax1.grid(True)

            fft = np.abs(np.fft.rfft(audio))
            freqs = np.fft.rfftfreq(len(audio), 1 / self.sample_rate)
            self.ax2.clear(); self.ax2.plot(freqs, fft, color='purple')
            self.ax2.set_title("Mic Spectrum"); self.ax2.set_xlim(0, 3000); self.ax2.grid(True)

            peak = np.max(fft)
            if peak < self.asi_threshold:
                self.mutate_frequency("Low resonance detected")

            self.ax1.figure.canvas.draw()

        with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate, blocksize=1024):
            while True: time.sleep(0.1)

    def listen_biometric(self):
        try:
            ser = serial.Serial('COM3', 9600)
            while True:
                line = ser.readline().decode().strip()
                bpm, eeg = map(float, line.split(','))
                self.bpm, self.eeg = bpm, eeg
                self.bio_panel.config(text=f"Heart Rate: {bpm} BPM | EEG Delta: {eeg} Hz")
                if self.running and bpm < 50:
                    self.mutate_frequency("Biometric stagnation detected")
        except Exception as e:
            self.log_msg(f"[ERROR] Biometric sensor not found: {e}")

    def mutate_frequency(self, reason):
        old_freq = self.current_freq
        self.current_freq += np.random.randint(-20, 20)
        self.narration.config(text=f"⚠️ ASI mutation: {old_freq} → {self.current_freq} Hz")
        self.log_msg(f"[ASI] {reason}. Mutating to {self.current_freq} Hz")
        self.play()

    def log_msg(self, msg):
        self.log.insert(tk.END, f"{time.strftime('%H:%M')} {msg}\n")
        self.log.see(tk.END)

if __name__ == "__main__":
    MagicBox().mainloop()

