# panels/codex_panel.py

import tkinter as tk

class CodexPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#222")
        self.text = tk.Text(self, bg="#111", fg="#0ff", font=("Courier", 10))
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, message):
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)

