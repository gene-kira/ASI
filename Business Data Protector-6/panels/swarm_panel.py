# panels/swarm_panel.py

import tkinter as tk

class SwarmPanel(tk.Frame):
    def __init__(self, parent, swarm_nodes, font_size=12):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)
        self.labels = {}

        title = tk.Label(self, text="🔄 Swarm Sync", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        for iface, label in swarm_nodes.items():
            lbl = tk.Label(self, text=f"{label}: Idle", fg="#0f0", bg="#111", font=self.font, anchor="w")
            lbl.pack(fill=tk.X, padx=5)
            self.labels[iface] = lbl

    def update_sync(self, iface, status):
        if iface in self.labels:
            self.labels[iface].config(text=f"{iface}: {status}")

