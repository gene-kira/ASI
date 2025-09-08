# panels/status_panel.py

import tkinter as tk

class StatusPanel(tk.Frame):
    def __init__(self, parent, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Courier", font_size)

        title = tk.Label(self, text="🩺 System Status", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        self.health_label = tk.Label(self, text="Status: Checking...", fg="#fff", bg="#111", font=self.font)
        self.health_label.pack(pady=2)

        self.emergency_label = tk.Label(self, text="", fg="#f00", bg="#111", font=self.font)
        self.emergency_label.pack(pady=2)

        self.port_label = tk.Label(self, text="Ports: Scanning...", fg="#0f0", bg="#111", font=self.font)
        self.port_label.pack(pady=2)

        self.enhancer_label = tk.Label(self, text="Enhancer: Idle", fg="#aaa", bg="#111", font=self.font)
        self.enhancer_label.pack(pady=2)

    def update_health(self, status, emergency=None):
        self.health_label.config(text=f"Status: {status}")
        self.emergency_label.config(text=f"⚠️ {emergency}" if emergency else "")

    def update_ports(self, ports):
        self.port_label.config(text=f"Ports: {', '.join(map(str, ports))}")

    def update_enhancer(self, status):
        self.enhancer_label.config(text=f"Enhancer: {status}")

