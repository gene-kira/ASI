# panels/traffic_monitor_panel.py

import tkinter as tk

class TrafficMonitorPanel(tk.Frame):
    def __init__(self, parent, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)
        self.labels = {}

        title = tk.Label(self, text="📡 Live Traffic Monitor", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

    def update_traffic(self, iface, sent_kbps, recv_kbps):
        if iface not in self.labels:
            lbl = tk.Label(self, text="", fg="#0f0", bg="#111", font=self.font, anchor="w")
            lbl.pack(fill=tk.X, padx=5)
            self.labels[iface] = lbl
        self.labels[iface].config(text=f"{iface}: ↑ {sent_kbps} KB/s | ↓ {recv_kbps} KB/s")

