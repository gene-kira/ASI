import tkinter as tk
from tkinter import ttk
import threading
import time
import random

class MythicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Mythic Cloak Node")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e2f")

        self.scan_interval = 60000  # Default: 60 seconds

        self.create_widgets()
        self.auto_scan_on_start()

    def create_widgets(self):
        title = tk.Label(self.root, text="Mythic Cloak Node", font=("Helvetica", 20, "bold"),
                         bg="#1e1e2f", fg="#00ffe7")
        title.pack(pady=10)

        self.output = tk.Text(self.root, height=15, bg="#2e2e3f", fg="#ffffff", font=("Consolas", 10))
        self.output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(self.root, bg="#1e1e2f")
        control_frame.pack(pady=5)

        scan_btn = tk.Button(control_frame, text="🔍 Manual Scan", command=self.manual_scan,
                             bg="#00ffe7", fg="#000000", font=("Helvetica", 10, "bold"))
        scan_btn.pack(side=tk.LEFT, padx=10)

        interval_label = tk.Label(control_frame, text="Scan Interval:", bg="#1e1e2f", fg="#ffffff")
        interval_label.pack(side=tk.LEFT)

        self.interval_var = tk.StringVar()
        interval_dropdown = ttk.Combobox(control_frame, textvariable=self.interval_var, state="readonly",
                                         values=["30s", "60s", "120s"])
        interval_dropdown.current(1)  # Default to 60s
        interval_dropdown.pack(side=tk.LEFT, padx=5)
        interval_dropdown.bind("<<ComboboxSelected>>", self.update_interval)

    def update_interval(self, event=None):
        val = self.interval_var.get()
        seconds = {"30s": 30000, "60s": 60000, "120s": 120000}
        self.scan_interval = seconds.get(val, 60000)
        self.output.insert(tk.END, f"⏱️ Scan interval set to {val}\n")

    def auto_scan_on_start(self):
        self.output.insert(tk.END, "🚀 Auto-scan initiated...\n")
        self.schedule_scan()

    def schedule_scan(self):
        threading.Thread(target=self.scan_and_defend, daemon=True).start()
        self.root.after(self.scan_interval, self.schedule_scan)

    def manual_scan(self):
        self.output.insert(tk.END, "🧭 Manual scan triggered...\n")
        threading.Thread(target=self.scan_and_defend, daemon=True).start()

    def scan_and_defend(self):
        threats = self.detect_threats()
        if threats:
            for threat in threats:
                self.output.insert(tk.END, f"⚠️ Threat detected: {threat}\n")
                self.defend(threat)
        else:
            self.output.insert(tk.END, "✅ No threats found.\n")

    def detect_threats(self):
        # Simulated threat detection
        time.sleep(1)
        return random.choices(["IP anomaly", "MAC spoof", "Vault breach", "Telemetry leak"], k=random.randint(0, 2))

    def defend(self, threat):
        self.output.insert(tk.END, f"🛡️ Neutralizing {threat}...\n")
        time.sleep(0.5)
        self.output.insert(tk.END, f"✨ {threat} neutralized.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MythicGUI(root)
    root.mainloop()

