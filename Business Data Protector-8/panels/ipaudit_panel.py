# panels/ip_audit_panel.py

import tkinter as tk
from tkinter import ttk

class IPAuditPanel(tk.Frame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent, bg="#111")
        self.font = ("Courier", font_size)

        # Title
        title = tk.Label(self, text="📜 Blocked IP Audit", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        # Scrollable frame
        frame = tk.Frame(self, bg="#111")
        frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(frame, bg="#111", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.log_frame = tk.Frame(self.canvas, bg="#111")

        self.log_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.log_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entries = []

    def log_block(self, ip, country):
        entry = tk.Label(
            self.log_frame,
            text=f"🚫 {ip} → {country}",
            fg="#0f0",
            bg="#111",
            anchor="w",
            font=self.font
        )
        entry.pack(fill=tk.X, padx=5, pady=2)
        self.entries.append(entry)

