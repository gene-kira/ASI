# panels/overlay_panel.py

import tkinter as tk

class OverlayPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#222")
        tk.Label(self, text="Overlay Panel (Future Expansion)", fg="#888", bg="#222").pack(pady=10)

