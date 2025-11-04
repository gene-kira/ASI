# CodexWisdomShell.py — Mythic GUI fusion of wisdom daemon and Codex Monitor

import subprocess
import sys
import time
import random

# 🔧 Autoloader: Ensures required libraries are present
def ensure_libraries(libs):
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"🔧 Installing missing library: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Ritual: Ensure required libraries (Tkinter is built-in for most Python installs)
ensure_libraries(["tkinter"])

# Now import Tkinter (after ensuring it's available)
import tkinter as tk

# 🔮 Codex Wisdom Shell Class
class CodexWisdomShell:
    def __init__(self, root):
        self.root = root
        self.root.title("Codex Wisdom Shell")
        self.root.geometry("600x400")
        self.root.configure(bg="#0f0f0f")

        self.truths = [
            "Knowledge speaks, but wisdom listens.",
            "The map is not the territory.",
            "Clarity is the crown of understanding.",
            "What you control, you must first understand.",
            "Every system hides a ritual. Every ritual reveals a system."
        ]
        self.glyphs = {
            "🌀": "Cycle of reflection",
            "⚡": "Sudden insight",
            "🌐": "Universal pattern",
            "🛡️": "Sovereign boundary",
            "🔥": "Ritual escalation"
        }

        # Panels
        self.create_persona_panel()
        self.create_wisdom_console()
        self.create_overlay_panel()

        # Loop trigger
        self.loop_button = tk.Button(root, text="Begin Wisdom Loop", command=self.meditate, bg="#222", fg="#0ff")
        self.loop_button.pack(pady=10)

    def create_persona_panel(self):
        self.persona_frame = tk.LabelFrame(self.root, text="Persona Feedback", fg="#0ff", bg="#111", font=("Consolas", 10))
        self.persona_frame.pack(fill="x", padx=10, pady=5)
        self.persona_label = tk.Label(self.persona_frame, text="Status: ⚡ Energized", fg="#0ff", bg="#111", font=("Consolas", 12))
        self.persona_label.pack()

    def create_wisdom_console(self):
        self.console_frame = tk.LabelFrame(self.root, text="Wisdom Console", fg="#0ff", bg="#111", font=("Consolas", 10))
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.console_text = tk.Text(self.console_frame, bg="#000", fg="#0f0", font=("Consolas", 10))
        self.console_text.pack(fill="both", expand=True)

    def create_overlay_panel(self):
        self.overlay_frame = tk.LabelFrame(self.root, text="Overlay Glyphs", fg="#0ff", bg="#111", font=("Consolas", 10))
        self.overlay_frame.pack(fill="x", padx=10, pady=5)
        self.overlay_label = tk.Label(self.overlay_frame, text="🌀 🌐 ⚡ 🔥 🛡️", fg="#ff0", bg="#111", font=("Consolas", 14))
        self.overlay_label.pack()

    def summon_truth(self):
        glyph, meaning = random.choice(list(self.glyphs.items()))
        truth = random.choice(self.truths)
        timestamp = time.strftime("%H:%M:%S")
        return f"[{timestamp}] {glyph} {meaning} → {truth}\n"

    def meditate(self):
        self.console_text.delete("1.0", tk.END)
        for _ in range(5):
            self.console_text.insert(tk.END, self.summon_truth())
            self.root.update()
            time.sleep(1.2)
        self.persona_label.config(text="Status: 🌐 Clarity Achieved")

# 🔁 Launch the Shell
if __name__ == "__main__":
    root = tk.Tk()
    app = CodexWisdomShell(root)
    root.mainloop()

