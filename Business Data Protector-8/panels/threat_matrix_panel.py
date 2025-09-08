# panels/threat_matrix_panel.py

import tkinter as tk
import time

class ThreatMatrixPanel(tk.Frame):
    def __init__(self, parent, memory, font_size=10):
        super().__init__(parent, bg="#ffffff")
        self.font = ("Segoe UI", font_size)

        title = tk.Label(self, text="Threat Matrix", font=("Segoe UI", font_size + 2, "bold"), bg="#ffffff", fg="#333")
        title.pack(anchor="w", padx=10, pady=(10, 0))

        frame = tk.Frame(self, bg="#ffffff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_box = tk.Text(frame, wrap=tk.WORD, bg="#fefefe", font=self.font)
        scrollbar = tk.Scrollbar(frame, command=self.log_box.yview)
        self.log_box.config(yscrollcommand=scrollbar.set)

        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        export_btn = tk.Button(self, text="📤 Export Threats", font=self.font, command=self.export_threats_to_file)
        export_btn.pack(anchor="e", padx=10, pady=(0, 10))

    def log_threat(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_box.see(tk.END)

    def export_threats_to_file(self, filename="threat_log.txt"):
        with open(filename, "w") as f:
            f.write(self.log_box.get("1.0", tk.END))

