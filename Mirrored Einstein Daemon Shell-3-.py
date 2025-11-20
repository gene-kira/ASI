import numpy as np
import time
from tkinter import Tk, Label, Button, filedialog, StringVar, ttk, Canvas

def simulate_tensor():
    return np.random.randn(4, 4) * np.random.uniform(0.8, 1.2) + np.random.normal(0, 0.1, (4, 4))

def invert_tensor(t): return -t
def compute_drift(a, b): return b - a

def classify_drift(d):
    if np.all(d < 0): return 'negative_energy'
    if np.any(d[:, 0] < 0): return 'time_reversal'
    if np.any(d[0, :] < 0): return 'parity_flip'
    return 'resurrection'

GLYPH_LABELS = {
    'negative_energy': "[Glyph] Negative Energy",
    'time_reversal': "[Glyph] Time Reversal",
    'parity_flip': "[Glyph] Parity Flip",
    'resurrection': "[Glyph] Resurrection"
}

class EinsteinShell:
    def __init__(self, root):
        self.root = root
        self.states = []
        self.root.title("Mirrored Einstein Daemon Shell")
        self.root.geometry("1000x600")
        self.drift_text = StringVar()
        self.glyph_text = StringVar()
        self.sync_text = StringVar()
        self.log_text = StringVar()
        self.codex_log_text = StringVar()
        self.build_gui()
        self.simulate()

    def build_gui(self):
        self.tab_control = ttk.Notebook(self.root)
        self.frames = {}
        for name in ['Drift', 'Glyph', 'Sync', 'Log', 'Codex']:
            frame = ttk.Frame(self.tab_control)
            self.frames[name] = frame
            self.tab_control.add(frame, text=name)
        self.tab_control.pack(expand=1, fill='both')

        # Drift tab
        Label(self.frames['Drift'], textvariable=self.drift_text, font=("Courier", 12), justify='left').grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        # Glyph tab
        Label(self.frames['Glyph'], textvariable=self.glyph_text, font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        # Sync tab
        Label(self.frames['Sync'], textvariable=self.sync_text, font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        # Log tab
        Label(self.frames['Log'], textvariable=self.log_text, font=("Courier", 10), justify='left', wraplength=900).grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        # Codex tab
        Label(self.frames['Codex'], text="Codex Glyph Sequence", font=("Arial", 16)).grid(row=0, column=0, pady=10)
        self.codex_canvas = Canvas(self.frames['Codex'], width=800, height=100, bg='black')
        self.codex_canvas.grid(row=1, column=0, padx=10)
        Label(self.frames['Codex'], textvariable=self.codex_log_text, font=("Courier", 10), justify='left', wraplength=900).grid(row=2, column=0, padx=10, pady=10, sticky='nw')

    def simulate(self):
        original = simulate_tensor()
        mirrored = invert_tensor(original)
        drift = compute_drift(original, mirrored)
        glyph = classify_drift(drift)
        self.states.append((original, mirrored, drift, glyph))
        self.update_gui(drift.tolist(), glyph)
        self.root.after(2000, self.simulate)

    def update_gui(self, drift, glyph):
        drift_str = "\n".join(" ".join(f"{float(v):+0.2f}" for v in row) for row in drift)
        self.drift_text.set(f"Curvature Drift Tensor:\n{drift_str}")
        self.glyph_text.set(GLYPH_LABELS.get(glyph, "[No Glyph]"))
        self.sync_text.set(f"Nodes synced: {len(self.states)}")
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] Glyph: {glyph}\n"
        self.log_text.set((self.log_text.get() + log_entry)[-3000:])  # Trim log if too long
        if glyph == 'resurrection':
            codex_entry = f"[{timestamp}] Resurrection glyph detected — Codex pulse triggered.\n"
            self.codex_log_text.set((self.codex_log_text.get() + codex_entry)[-3000:])
            self.render_codex()

    def render_codex(self):
        self.codex_canvas.delete("all")
        glyphs = ['💀','⚔️','🛡️','⚠️','🜏','🕊️','🔱','🔺']
        for i, g in enumerate(glyphs):
            try:
                self.codex_canvas.create_text(50+i*90, 50, text=g, font=("Segoe UI Emoji", 36), fill="white")
            except:
                self.codex_canvas.create_text(50+i*90, 50, text=g, font=("Arial", 36), fill="white")

if __name__ == "__main__":
    root = Tk()
    EinsteinShell(root)
    root.mainloop()

