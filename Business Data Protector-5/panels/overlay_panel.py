# panels/overlay_panel.py

import tkinter as tk

class OverlayPanel(tk.Frame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)

        title = tk.Label(self, text="🌀 Overlay Status", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        self.overlay_label = tk.Label(self, text="Overlay: Passive", fg="#0f0", bg="#111", font=self.font)
        self.overlay_label.pack(pady=2)

    def set_overlay(self, status):
        self.overlay_label.config(text=f"Overlay: {status}")

