# panels/codex_dashboard_panel.py

import tkinter as tk
import time

class CodexDashboardPanel(tk.Frame):
    def __init__(self, parent, font_size=10):
        super().__init__(parent, bg="#ffffff")
        self.font = ("Segoe UI", font_size)

        title = tk.Label(self, text="Codex Dashboard", font=("Segoe UI", font_size + 2, "bold"), bg="#ffffff", fg="#333")
        title.pack(anchor="w", padx=10, pady=(10, 0))

        frame = tk.Frame(self, bg="#ffffff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.codex_box = tk.Text(frame, wrap=tk.WORD, bg="#fefefe", font=self.font)
        scrollbar = tk.Scrollbar(frame, command=self.codex_box.yview)
        self.codex_box.config(yscrollcommand=scrollbar.set)

        self.codex_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        export_btn = tk.Button(self, text="📤 Export Codex", font=self.font, command=self.export_codex_to_file)
        export_btn.pack(anchor="e", padx=10, pady=(0, 10))

    def load_codex(self, codex_entries):
        self.codex_box.delete("1.0", tk.END)
        for entry in codex_entries:
            if isinstance(entry, dict):
                line = f"[{entry.get('timestamp')}] {entry.get('label')} — Source: {entry.get('source')}\n"
                self.codex_box.insert(tk.END, line)
        self.codex_box.see(tk.END)

    def export_codex_to_file(self, filename="codex_log.txt"):
        with open(filename, "w") as f:
            f.write(self.codex_box.get("1.0", tk.END))

