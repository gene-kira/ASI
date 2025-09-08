# panels/threat_matrix_panel.py

import tkinter as tk
import math
import psutil
from persona_engine import inject_persona

class ThreatMatrixPanel(tk.Frame):
    def __init__(self, parent, memory):
        super().__init__(parent, bg="#111")
        self.memory = memory
        self.canvas = tk.Canvas(self, bg="#111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.bind("<Configure>", lambda e: self.update_matrix())

    def update_matrix(self):
        self.canvas.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        center_x = width // 2
        center_y = height // 2

        connections = psutil.net_connections(kind='inet')
        ips = set()
        for conn in connections:
            if conn.raddr:
                ips.add(conn.raddr.ip)

        if not ips:
            self.canvas.create_text(center_x, center_y, text="No active IPs", fill="#888", font=("Courier", 12))
            return

        radius = min(width, height) // 3
        angle_step = 360 / len(ips)

        for i, ip in enumerate(sorted(ips)):
            angle = math.radians(angle_step * i)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            persona = inject_persona(self.memory)
            color = "#0f0" if ip in self.memory.get("allowed", []) else "#f00" if ip in self.memory.get("blocked", []) else "#888"
            label = f"{ip}\n{persona}"

            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, outline="#222")
            self.canvas.create_text(x, y+30, text=label, fill="#0ff", font=("Courier", 9), justify="center")

