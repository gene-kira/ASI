# 🔮 MagicBox Memory Dashboard (Full Mythic Edition)
import os, sys, threading, time, subprocess

# 🧰 Auto-loader for required libraries
def autoload():
    required = ['psutil', 'tkinter', 'PIL', 'yaml', 'cryptography']
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
from cryptography.fernet import Fernet

# 📜 Config (inline for simplicity)
CONFIG = {
    'panels': [
        {'id': 'glyphGrid', 'enabled': True, 'glyphStyle': 'mythic', 'updateRate': 1000},
        {'id': 'heatmapOverlay', 'enabled': True, 'colorScheme': 'plasma'},
        {'id': 'trailRenderer', 'enabled': True, 'trailLength': 128},
        {'id': 'mutationTimeline', 'enabled': True, 'replaySpeed': 1.0},
        {'id': 'threatSim', 'enabled': True},
        {'id': 'vaultSync', 'enabled': True}
    ]
}

# 🔐 VaultSyncEngine
class VaultSync:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.cipher.decrypt(token.encode()).decode()

vault = VaultSync()

# 🧠 Memory Telemetry
def get_memory_snapshot():
    ram = psutil.virtual_memory()
    mutations = [
        {'address': 0xDEADBEEF, 'size': 4096, 'timestamp': time.time(), 'type': 'allocation'},
        {'address': 0xFEEDBEEF, 'size': 2048, 'timestamp': time.time(), 'type': 'mutation'}
    ]
    if CONFIG['panels'][4]['enabled']:  # threatSim
        mutations.append({'address': 0xBADF00D, 'size': 1024, 'timestamp': time.time(), 'type': 'threat'})
    return {
        'ram_used': ram.used // (1024 * 1024),
        'ram_total': ram.total // (1024 * 1024),
        'vram_used': 2048,
        'vram_total': 8192,
        'mutations': mutations
    }

# 🎨 Glyph Renderer
class GlyphCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='black', **kwargs)
        self.glyphs = []
        self.trails = []

    def spawn_glyph(self, x, y, state):
        color = self.get_color(state)
        radius = 10
        glyph = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        self.glyphs.append(glyph)
        if CONFIG['panels'][2]['enabled']:
            trail = self.create_line(x, y, x, y+20, fill=color)
            self.trails.append(trail)

    def get_color(self, state):
        return {
            'stable': '#00ff00',
            'mutating': '#0000ff',
            'threat': '#ff0000'
        }.get(state, '#ffffff')

    def update_glyphs(self, snapshot):
        self.delete("all")
        for i, mutation in enumerate(snapshot['mutations']):
            x = 50 + (i * 60)
            y = 100
            state = 'mutating' if mutation['type'] == 'mutation' else 'stable'
            if mutation['type'] == 'threat':
                state = 'threat'
            self.spawn_glyph(x, y, state)

# 🖼️ Heatmap Overlay
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

# 🌀 Mutation Timeline
class TimelinePanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='black')
        self.label = tk.Label(self, text="Mutation Timeline", fg='white', bg='black')
        self.label.pack()
        self.log = tk.Text(self, height=5, bg='black', fg='white')
        self.log.pack()

    def update_timeline(self, snapshot):
        self.log.delete(1.0, tk.END)
        for m in snapshot['mutations']:
            line = f"{time.strftime('%H:%M:%S', time.localtime(m['timestamp']))} | {m['type']} @ {hex(m['address'])} | {m['size']} bytes\n"
            if CONFIG['panels'][5]['enabled']:
                line = vault.encrypt(line)
            self.log.insert(tk.END, line + "\n")

# 🧙 MagicBox GUI
class MagicBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧙 MagicBox Memory Dashboard")
        self.geometry("900x700")
        self.configure(bg='black')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", foreground='green', background='green')

        self.glyph_canvas = GlyphCanvas(self, width=900, height=250)
        self.glyph_canvas.pack()

        self.heatmap = HeatmapPanel(self)
        self.heatmap.pack(pady=10)

        self.timeline = TimelinePanel(self)
        self.timeline.pack(pady=10)

        self.update_loop()

    def update_loop(self):
        snapshot = get_memory_snapshot()
        self.glyph_canvas.update_glyphs(snapshot)
        self.heatmap.update_heatmap(snapshot)
        self.timeline.update_timeline(snapshot)
        self.after(CONFIG['panels'][0]['updateRate'], self.update_loop)

# 🚀 Launch
if __name__ == "__main__":
    MagicBoxApp().mainloop()

