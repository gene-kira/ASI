# panels/status_panel.py

import tkinter as tk
from tkinter import ttk

class StatusPanel(tk.Frame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)
        self.port_labels = []

        title = tk.Label(self, text="🧩 System Status", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        self.health_label = tk.Label(self, text="Health: Checking...", fg="#0f0", bg="#111", font=self.font)
        self.health_label.pack(pady=2)

        self.enhancer_label = tk.Label(self, text="Enhancer: Idle", fg="#888", bg="#111", font=self.font)
        self.enhancer_label.pack(pady=2)

        # Scrollable port frame
        port_frame = tk.Frame(self, bg="#111")
        port_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(port_frame, bg="#111", highlightthickness=0)
        scrollbar = ttk.Scrollbar(port_frame, orient="vertical", command=canvas.yview)
        self.port_container = tk.Frame(canvas, bg="#111")

        self.port_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.port_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_health(self, status, emergency=None):
        self.health_label.config(text=f"Health: {status}")
        self.health_label.config(fg="#f00" if emergency else "#0f0")

    def update_enhancer(self, status):
        self.enhancer_label.config(text=f"Enhancer: {status}")

    def update_ports(self, ports):
        for label in self.port_labels:
            label.destroy()
        self.port_labels.clear()

        for port in sorted(set(ports)):
            lbl = tk.Label(self.port_container, text=f"Port {port}", fg="#0ff", bg="#111", anchor="w", font=self.font)
            lbl.pack(fill=tk.X, padx=5)
            self.port_labels.append(lbl)

