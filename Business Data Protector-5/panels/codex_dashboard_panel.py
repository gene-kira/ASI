# panels/codex_dashboard_panel.py

import tkinter as tk

class CodexDashboardPanel(tk.Frame):
    def __init__(self, parent, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Courier", font_size)

        title = tk.Label(self, text="📘 Codex Dashboard", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        self.codex_box = tk.Text(self, bg="#000", fg="#0ff", height=10, font=self.font)
        self.codex_box.pack(fill=tk.BOTH, expand=True)

    def load_codex(self, memory):
        self.codex_box.delete("1.0", tk.END)

        if not memory:
            self.codex_box.insert(tk.END, "📭 No codex entries found.\n")
            return

        for entry in memory:
            if isinstance(entry, dict):
                timestamp = entry.get("timestamp", "⏱️")
                event = entry.get("event", "Unknown")
                self.codex_box.insert(tk.END, f"{timestamp} | {event}\n")
            else:
                self.codex_box.insert(tk.END, f"⚠️ Invalid entry: {str(entry)}\n")

        self.codex_box.see(tk.END)

