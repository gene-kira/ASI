# panels/codex_dashboard_panel.py

import tkinter as tk
from tkinter import ttk

class CodexDashboardPanel(tk.Frame):
    def __init__(self, parent, codex_file="codex.log"):
        super().__init__(parent, bg="#111")
        self.codex_file = codex_file

        title = tk.Label(self, text="📜 Codex Mutation Dashboard", fg="#0ff", bg="#111", font=("Helvetica", 12))
        title.pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Timestamp", "Event"), show="headings", style="Treeview")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Event", text="Event")
        self.tree.column("Timestamp", width=180)
        self.tree.column("Event", width=600)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.refresh_button = tk.Button(self, text="🔄 Refresh", command=self.load_codex, bg="#222", fg="#0ff")
        self.refresh_button.pack(pady=5)

        self.load_codex()

    def load_codex(self):
        self.tree.delete(*self.tree.get_children())
        try:
            with open(self.codex_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        timestamp, event = self._split_entry(line.strip())
                        self.tree.insert("", tk.END, values=(timestamp, event))
        except Exception as e:
            self.tree.insert("", tk.END, values=("Error", str(e)))

    def _split_entry(self, line):
        if line.startswith("[") and "]" in line:
            ts_end = line.index("]")
            timestamp = line[1:ts_end]
            event = line[ts_end+2:]
            return timestamp, event
        return "Unknown", line

