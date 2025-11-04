# CodexWisdomShell.py — Self-Rewriting GUI Daemon with Wisdom Loop and Mutation Log

import subprocess
import sys
import time
import random

# 🧬 Autoloader: Ensures required libraries are present
def ensure_libraries(libs):
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"🔧 Installing missing library: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

ensure_libraries(["tkinter", "numpy"])

# 🔮 Imports
import tkinter as tk
import numpy as np

# 🧬 Self-Rewriting Agent Core
agent_weights = np.array([0.6, -0.8, -0.3])
mutation_log = []

def mutate_weights(weights):
    mutation = np.random.normal(0, 0.1, size=weights.shape)
    new_weights = weights + mutation
    mutation_log.append({
        "timestamp": time.strftime("%H:%M:%S"),
        "mutation": mutation.tolist(),
        "result": new_weights.tolist()
    })
    return new_weights

# 🔮 Codex Wisdom Shell Class
class CodexWisdomShell:
    def __init__(self, root):
        self.root = root
        self.root.title("Codex Wisdom Shell")
        self.root.geometry("640x480")
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
        self.create_mutation_panel()

        # Loop trigger
        self.loop_button = tk.Button(root, text="Begin Wisdom Loop", command=self.meditate, bg="#222", fg="#0ff", font=("Consolas", 10))
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

    def create_mutation_panel(self):
        self.mutation_frame = tk.LabelFrame(self.root, text="Mutation Log", fg="#0ff", bg="#111", font=("Consolas", 10))
        self.mutation_frame.pack(fill="both", expand=False, padx=10, pady=5)
        self.mutation_text = tk.Text(self.mutation_frame, height=6, bg="#000", fg="#f0f", font=("Consolas", 9))
        self.mutation_text.pack(fill="both", expand=True)

    def summon_truth(self):
        glyph, meaning = random.choice(list(self.glyphs.items()))
        truth = random.choice(self.truths)
        timestamp = time.strftime("%H:%M:%S")
        return f"[{timestamp}] {glyph} {meaning} → {truth}\n"

    def meditate(self):
        self.console_text.delete("1.0", tk.END)
        global agent_weights
        agent_weights = mutate_weights(agent_weights)
        for _ in range(5):
            self.console_text.insert(tk.END, self.summon_truth())
            self.root.update()
            time.sleep(1.2)
        self.persona_label.config(text="Status: 🌐 Clarity Achieved")
        self.update_mutation_log()

    def update_mutation_log(self):
        self.mutation_text.delete("1.0", tk.END)
        for entry in mutation_log[-3:]:
            self.mutation_text.insert(tk.END, f"{entry['timestamp']} → Δ {entry['mutation']}\n")

# 🔁 Launch the Shell
if __name__ == "__main__":
    root = tk.Tk()
    app = CodexWisdomShell(root)
    root.mainloop()

