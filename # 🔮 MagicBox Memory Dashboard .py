# 🔮 MagicBox Memory Dashboard (One-click edition)
import os, sys, threading, time

# 🧰 Auto-loader for required libraries
def autoload():
    import subprocess
    required = ['psutil', 'tkinter', 'PIL', 'yaml']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload()

# 🧠 Imports after auto-loader
import psutil
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import yaml

# 📜 Config (inline for simplicity)
CONFIG = {
    'panels': [
        {'id': 'glyphGrid', 'enabled': True, 'glyphStyle': 'mythic', 'updateRate': 1000},
        {'id': 'heatmapOverlay', 'enabled': True, 'colorScheme': 'plasma'},
        {'id': 'trailRenderer', 'enabled': True, 'trailLength': 128},
        {'id': 'mutationTimeline', 'enabled': True, 'replaySpeed': 1.0},
        {'id': 'threatSim', 'enabled': False}
    ]
}

# 🧠 Memory Telemetry
def get_memory_snapshot():
    ram = psutil.virtual_memory()
    return {
        'ram_used': ram.used // (1024 * 1024),
        'ram_total': ram.total // (1024 * 1024),
        'vram_used': 2048,  # Stub value
        'vram_total': 8192, # Stub value
        'mutations': [
            {'address': 0xDEADBEEF, 'size': 4096, 'timestamp': time.time(), 'type': 'allocation'}
        ]
    }

# 🎨 Glyph Renderer
class GlyphCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='black', **kwargs)
        self.glyphs = []

    def spawn_glyph(self, x, y, state):
        color = self.get_color(state)
        radius = 10
        glyph = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        self.glyphs.append(glyph)

    def get_color(self, state):
        return {
            'stable': '#00ff00',
            'mutating': '#0000ff',
            'threat': '#ff0000'
        }.get(state, '#ffffff')

    def update_glyphs(self, snapshot):
        self.delete("all")
        for i, mutation in enumerate(snapshot['mutations']):
            x = 50 + (i * 30)
            y = 100
            state = 'mutating' if mutation['type'] == 'allocation' else 'stable'
            self.spawn_glyph(x, y, state)

# 🖼️ Heatmap Overlay (simple RAM usage bar)
class HeatmapPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='black')
        self.label = tk.Label(self, text="Memory Heatmap", fg='white', bg='black')
        self.label.pack()
        self.bar = ttk.Progressbar(self, orient='horizontal', length=300, mode='determinate')
        self.bar.pack()

    def update_heatmap(self, snapshot):
        percent = int((snapshot['ram_used'] / snapshot['ram_total']) * 100)
        self.bar['value'] = percent
        self.label.config(text=f"RAM Usage: {percent}%")

# 🌀 Trail Renderer (stubbed for now)
class TrailPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='black')
        self.label = tk.Label(self, text="Trail Renderer (coming soon)", fg='gray', bg='black')
        self.label.pack()

# 🧙 MagicBox GUI
class MagicBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧙 MagicBox Memory Dashboard")
        self.geometry("800x600")
        self.configure(bg='black')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", foreground='green', background='green')

        self.glyph_canvas = GlyphCanvas(self, width=800, height=200)
        self.glyph_canvas.pack()

        self.heatmap = HeatmapPanel(self)
        self.heatmap.pack(pady=10)

        self.trail_panel = TrailPanel(self)
        self.trail_panel.pack(pady=10)

        self.update_loop()

    def update_loop(self):
        snapshot = get_memory_snapshot()
        self.glyph_canvas.update_glyphs(snapshot)
        self.heatmap.update_heatmap(snapshot)
        self.after(CONFIG['panels'][0]['updateRate'], self.update_loop)

# 🚀 Launch
if __name__ == "__main__":
    MagicBoxApp().mainloop()

