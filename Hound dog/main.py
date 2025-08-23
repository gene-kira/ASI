import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil

from config import MAGICBOX_COLORS
from voice import speak
from vault import log_threat_to_memory
from glyphs import spawn_glyph, animate_glyphs
from monitor import monitor_processes
from tabs import create_tabs
from components import build_text_panel, build_voice_panel, build_config_panel

class MagicBoxSentinel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 MagicBox Sentinel — Mythic ASI Edition")
        self.geometry("1200x800")
        self.configure(bg=MAGICBOX_COLORS["bg"])
        self.trust_threshold = 3
        self.glyphs = []

        self.build_gui()
        self.create_status_pulse()
        self.start_listeners()

    def build_gui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')
        create_tabs(self, notebook)

        self.process_output = build_text_panel(self.watchtower_tab, "Live Process Scan")
        self.ip_output = build_text_panel(self.ip_tracker_tab, "Foreign IP Tracker")
        self.threat_output = build_text_panel(self.threat_tab, "Threat Response Console")
        self.mutation_output = build_text_panel(self.mutation_tab, "Mutation Trail Logs")

        build_voice_panel(self.voice_tab)
        _, self.threshold_label = build_config_panel(self.config_tab, self.trust_threshold, self.update_threshold)

        self.canvas = tk.Canvas(self.glyph_tab, bg=MAGICBOX_COLORS["bg"])
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.animate_glyphs()

    def update_threshold(self, val):
        self.trust_threshold = int(float(val))
        self.threshold_label.config(text=f"Kill Threshold: {self.trust_threshold}")

    def animate_glyphs(self):
        animate_glyphs(self.canvas, self.glyphs)
        self.after(100, self.animate_glyphs)

    def create_status_pulse(self):
        self.status_label = tk.Label(self, text="🟢 Sentinel Active", bg=MAGICBOX_COLORS["bg"], fg=MAGICBOX_COLORS["safe"], font=("Helvetica", 12))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        def pulse():
            while True:
                now = time.strftime("%H:%M:%S")
                self.status_label.config(text=f"🟢 Sentinel Active — Last scan: {now}")
                time.sleep(5)

        threading.Thread(target=pulse, daemon=True).start()

    def start_listeners(self):
        threading.Thread(target=monitor_processes, args=(self,), daemon=True).start()

    def predictive_cloak(self, pid, name):
        msg = f"🌀 Cloaking {name} (PID {pid}) — anomaly detected\n"
        self.threat_output.insert("end", msg)
        self.mutation_output.insert("end", f"🧬 Mutation: {name} cloaked\n")
        speak(f"{name} cloaked for observation.")
        spawn_glyph(self.glyphs, MAGICBOX_COLORS["accent"])

    def terminate_process(self, pid, name):
        try:
            psutil.Process(pid).terminate()
            msg = f"💀 Terminated {name} (PID {pid}) — exceeded trust threshold\n"
            self.threat_output.insert("end", msg)
            self.mutation_output.insert("end", f"🧬 Mutation: {name} terminated\n")
            speak(f"{name} has been terminated. No fear.")
            spawn_glyph(self.glyphs, MAGICBOX_COLORS["danger"])
        except Exception as e:
            self.threat_output.insert("end", f"⚠️ Failed to terminate {name}: {e}\n")

if __name__ == "__main__":
    app = MagicBoxSentinel()
    app.mainloop()

