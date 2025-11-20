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
        self.root.title("Codex Purge Shell — Mirrored Einstein Daemon")
        self.root.geometry("1200x800")
        self.drift_text = StringVar()
        self.sync_text = StringVar()
        self.glyph_text = StringVar()
        self.formula_text = StringVar()
        self.log_text = StringVar()
        self.codex_log_text = StringVar()
        self.build_gui()
        self.simulate()

    def build_gui(self):
        self.tab_control = ttk.Notebook(self.root)
        self.frames = {}
        for name in ['Drift', 'Glyph', 'Sync', 'Formulas', 'Log', 'Codex', 'Export']:
            frame = ttk.Frame(self.tab_control)
            self.frames[name] = frame
            self.tab_control.add(frame, text=name)
        self.tab_control.pack(expand=1, fill='both')

        Label(self.frames['Drift'], textvariable=self.drift_text, font=("Courier", 12), justify='left').grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        Label(self.frames['Glyph'], textvariable=self.glyph_text, font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        Label(self.frames['Sync'], textvariable=self.sync_text, font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        Label(self.frames['Formulas'], textvariable=self.formula_text, font=("Courier", 11), justify='left').grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        Label(self.frames['Log'], textvariable=self.log_text, font=("Courier", 10), justify='left', wraplength=1000).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        Label(self.frames['Codex'], text="Codex Glyph Sequence", font=("Arial", 16)).grid(row=0, column=0, pady=10)
        self.codex_canvas = Canvas(self.frames['Codex'], width=900, height=100, bg='black')
        self.codex_canvas.grid(row=1, column=0, padx=10)
        Label(self.frames['Codex'], textvariable=self.codex_log_text, font=("Courier", 10), justify='left', wraplength=1000).grid(row=2, column=0, padx=10, pady=10, sticky='nw')
        Button(self.frames['Export'], text="Export Drift Snapshot", command=self.export_drift).grid(row=0, column=0, padx=20, pady=20)

    def simulate(self):
        nodes = [simulate_tensor() for _ in range(3)]
        mirrored = [invert_tensor(t) for t in nodes]
        drifts = [compute_drift(a, b) for a, b in zip(nodes, mirrored)]
        glyphs = [classify_drift(d) for d in drifts]
        self.states.append((nodes, mirrored, drifts, glyphs))
        self.update_gui(drifts, glyphs)
        self.root.after(2000, self.simulate)

    def update_gui(self, drifts, glyphs):
        drift_str = "\n\n".join(
            f"Node {i+1} Drift:\n" + "\n".join(" ".join(f"{float(v):+0.2f}" for v in row) for row in d)
            for i, d in enumerate(drifts)
        )
        self.drift_text.set(drift_str)
        glyph_summary = "\n".join([f"Node {i+1}: {GLYPH_LABELS.get(g, g)}" for i, g in enumerate(glyphs)])
        self.glyph_text.set(glyph_summary)
        self.sync_text.set(f"Swarm nodes synced: {len(self.states)}")
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] Glyphs: {', '.join(glyphs)}\n"
        self.log_text.set((self.log_text.get() + log_entry)[-3000:])
        self.update_formulas()
        if 'resurrection' in glyphs:
            codex_entry = f"[{timestamp}] Resurrection glyph detected — Codex pulse triggered.\n"
            self.codex_log_text.set((self.codex_log_text.get() + codex_entry)[-3000:])
            self.render_codex()

    def update_formulas(self):
        eq1 = "Rμν - ½Rgμν + Λgμν = (8πG/c⁴)Tμν"
        eq2 = "-Rμν + ½Rgμν - Λgμν = -(8πG/c⁴)Tμν"
        self.formula_text.set(f"Original:\n  {eq1}\n\nMirrored:\n  {eq2}")

    def render_codex(self):
        self.codex_canvas.delete("all")
        glyphs = ['💀','⚔️','🛡️','⚠️','🜏','🕊️','🔱','🔺']
        for i, g in enumerate(glyphs):
            try:
                self.codex_canvas.create_text(50+i*100, 50, text=g, font=("Segoe UI Emoji", 36), fill="white")
            except:
                self.codex_canvas.create_text(50+i*100, 50, text=g, font=("Arial", 36), fill="white")

    def export_drift(self):
        if not self.states: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, "w") as f:
                f.write("timestamp,node,glyph,tensor_drift\n")
                for i, (nodes, mirrored, drifts, glyphs) in enumerate(self.states):
                    for j, (d, g) in enumerate(zip(drifts, glyphs)):
                        flat = ",".join(f"{float(v):.4f}" for row in d.tolist() for v in row)
                        f.write(f"{i},{j+1},{g},{flat}\n")

if __name__ == "__main__":
    root = Tk()
    EinsteinShell(root)
    root.mainloop()

