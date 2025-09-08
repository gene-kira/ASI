# panels/threat_matrix_panel.py

import tkinter as tk

class ThreatMatrixPanel(tk.Frame):
    def __init__(self, parent, memory, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Courier", font_size)
        self.memory = memory

        title = tk.Label(self, text="⚠️ Threat Matrix", fg="#f00", bg="#111", font=self.font)
        title.pack(pady=5)

        self.matrix_box = tk.Text(self, bg="#000", fg="#f00", height=10, font=self.font)
        self.matrix_box.pack(fill=tk.BOTH, expand=True)

    def log_threat(self, message):
        self.matrix_box.insert(tk.END, f"{message}\n")
        self.matrix_box.see(tk.END)

