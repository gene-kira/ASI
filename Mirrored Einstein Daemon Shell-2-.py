import subprocess
import sys
import os

# === Autoloader ===
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import numpy as np
except ImportError:
    install("numpy")
    import numpy as np

try:
    import tkinter as tk
    from tkinter import ttk, filedialog
except ImportError:
    install("tk")
    import tkinter as tk
    from tkinter import ttk, filedialog

try:
    from tkinterweb import HtmlFrame
except ImportError:
    install("tkinterweb")
    from tkinterweb import HtmlFrame

import threading
import time
import random

# === CPT Inversion Engine ===
def invert_tensor(tensor):
    return -1 * tensor

def simulate_curvature_tensor(intensity=1.0):
    base = np.random.randn(4, 4)
    noise = np.random.normal(0, 0.1, (4, 4))
    return base * intensity + noise

def compute_drift(original, mirrored):
    return mirrored - original

def classify_glyph(drift):
    if np.all(drift < 0):
        return 'negative_energy'
    elif np.any(drift[:, 0] < 0):
        return 'time_reversal'
    elif np.any(drift[0, :] < 0):
        return 'parity_flip'
    else:
        return 'resurrection'

# === SVG Glyphs ===
SVG_GLYPHS = {
    'negative_energy': '''
    <svg viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="20" fill="red">
        <animate attributeName="r" values="20;25;20" dur="1s" repeatCount="indefinite"/>
      </circle>
    </svg>
    ''',
    'time_reversal': '''
    <svg viewBox="0 0 100 100">
      <path d="M50,10 A40,40 0 1,1 49.9,10" fill="none" stroke="blue" stroke-width="4">
        <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="2s" repeatCount="indefinite"/>
      </path>
    </svg>
    ''',
    'parity_flip': '''
    <svg viewBox="0 0 100 100">
      <polygon points="30,50 50,30 50,70" fill="gold"/>
      <polygon points="70,50 50,30 50,70" fill="gold">
        <animateTransform attributeName="transform" type="scale" values="1,1;-1,1;1,1" dur="1.5s" repeatCount="indefinite"/>
      </polygon>
    </svg>
    ''',
    'resurrection': '''
    <svg viewBox="0 0 100 100">
      <circle cx="30" cy="50" r="10" fill="violet"/>
      <circle cx="70" cy="50" r="10" fill="violet"/>
      <line x1="30" y1="50" x2="70" y2="50" stroke="violet" stroke-width="2">
        <animate attributeName="stroke-width" values="2;5;2" dur="1s" repeatCount="indefinite"/>
      </line>
    </svg>
    '''
}

# === GUI Shell ===
class EinsteinShellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mirrored Einstein Daemon Shell")
        self.root.geometry("1200x800")
        self.build_gui()
        self.running = True
        self.node_states = []
        threading.Thread(target=self.simulate_loop, daemon=True).start()

    def build_gui(self):
        self.tab_control = ttk.Notebook(self.root)

        self.drift_tab = ttk.Frame(self.tab_control)
        self.glyph_tab = ttk.Frame(self.tab_control)
        self.sync_tab = ttk.Frame(self.tab_control)
        self.log_tab = ttk.Frame(self.tab_control)
        self.formula_tab = ttk.Frame(self.tab_control)
        self.export_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.drift_tab, text='Curvature Drift')
        self.tab_control.add(self.glyph_tab, text='Glyph Overlay')
        self.tab_control.add(self.sync_tab, text='Node Consensus')
        self.tab_control.add(self.log_tab, text='Resonance Log')
        self.tab_control.add(self.formula_tab, text='Symbolic Formulas')
        self.tab_control.add(self.export_tab, text='Export')

        self.tab_control.pack(expand=1, fill='both')

        self.drift_label = tk.Label(self.drift_tab, text="", font=("Courier", 12), justify='left')
        self.drift_label.pack(padx=10, pady=10)

        self.svg_frame = HtmlFrame(self.glyph_tab, messages_enabled=False)
        self.svg_frame.pack(fill="both", expand=True)

        self.sync_status = tk.Label(self.sync_tab, text="Syncing planetary nodes...", font=("Arial", 14))
        self.sync_status.pack(pady=20)

        self.log_box = tk.Text(self.log_tab, height=20, width=100)
        self.log_box.pack(padx=10, pady=10)

        self.formula_view = HtmlFrame(self.formula_tab, messages_enabled=False)
        self.formula_view.pack(fill="both", expand=True)

        self.export_button = tk.Button(self.export_tab, text="Export Drift Snapshot", command=self.export_drift)
        self.export_button.pack(pady=20)

    def simulate_loop(self):
        while self.running:
            original = simulate_curvature_tensor(intensity=random.uniform(0.8, 1.2))
            mirrored = invert_tensor(original)
            drift = compute_drift(original, mirrored)
            glyph_key = classify_glyph(drift)
            svg = SVG_GLYPHS.get(glyph_key, "<svg><text x='10' y='50'>No Glyph</text></svg>")
            self.node_states.append((original, mirrored, drift, glyph_key))
            self.update_gui(drift, svg, glyph_key)
            time.sleep(2)

    def update_gui(self, drift, svg, glyph_key):
        drift_str = "\n".join([" ".join(f"{val:+.2f}" for val in row) for row in drift])
        self.drift_label.config(text=f"Curvature Drift Tensor:\n{drift_str}")
        self.svg_frame.load_html(svg)
        self.sync_status.config(text=f"Nodes synced: {len(self.node_states)}")
        timestamp = time.strftime('%H:%M:%S')
        self.log_box.insert(tk.END, f"[{timestamp}] Glyph: {glyph_key}\n")
        self.log_box.see(tk.END)
        self.update_formula_panel()

    def update_formula_panel(self):
        latex_original = r"R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}"
        latex_mirrored = r"-R_{\mu\nu} + \frac{1}{2}Rg_{\mu\nu} - \Lambda g_{\mu\nu} = -\frac{8\pi G}{c^4}T_{\mu\nu}"
        html = f"""
        <html>
        <head>
          <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
          <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>
          <div style='font-size: 20px; padding: 20px;'>
            <p><strong>Original:</strong></p>
            $$ {latex_original} $$
            <p><strong>Mirrored:</strong></p>
            $$ {latex_mirrored} $$
          </div>
        </body>
        </html>
        """
        self.formula_view.load_html(html)

    def export_drift(self):
        if not self.node_states:
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, "w") as f:
                f.write("timestamp,glyph,tensor_drift\n")
                for i, (orig, mirr, drift, glyph) in enumerate(self.node_states):
                    flat_drift = ",".join(f"{val:.4f}" for row in drift for val in row)
                    f.write(f"{i},{glyph},{flat_drift}\n")

# === Launch Daemon ===
def launch_daemon():
    root = tk.Tk()
    app = EinsteinShellGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_daemon()



    
