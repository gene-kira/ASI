# 🔮 MagicBox Memory Dashboard (AI-Powered Edition)
import os, sys, threading, time, subprocess, random

# 🧰 Auto-loader for required libraries
def autoload():
    required = ['psutil', 'tkinter', 'PIL', 'yaml', 'cryptography', 'sklearn']
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
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# 📜 Config (inline for simplicity)
CONFIG = {
    'panels': [
        {'id': 'glyphGrid', 'enabled': True, 'glyphStyle': 'mythic', 'updateRate': 1000},
        {'id': 'heatmapOverlay', 'enabled': True, 'colorScheme': 'plasma'},
        {'id': 'trailRenderer', 'enabled': True, 'trailLength': 128},
        {'id': 'mutationTimeline', 'enabled': True, 'replaySpeed': 1.0},
        {'id': 'threatSim', 'enabled': True},
        {'id': 'vaultSync', 'enabled': True},
        {'id': 'swarmClustering', 'enabled': True},
        {'id': 'predictiveRouting', 'enabled': True},
        {'id': 'aiRouting', 'enabled': True}
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

# 🧠 AI Predictive Model
class AIPredictor:
    def __init__(self):
        self.model = DecisionTreeClassifier()
        self.train()

    def train(self):
        # Training data: [size, type_code] => zone
        X = [
            [4096, 0],  # allocation
            [2048, 1],  # mutation
            [1024, 2],  # threat
            [8192, 0],
            [512, 2]
        ]
        y = [0, 1, 2, 0, 2]  # zones: 0=left, 1=center, 2=right
        self.model.fit(X, y)

    def predict_zone(self, size, type_):
        type_code = {'allocation': 0, 'mutation': 1, 'threat': 2}.get(type_, 0)
        zone = self.model.predict([[size, type_code]])[0]
        return zone

ai = AIPredictor()

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

# 🧠 Swarm Clustering + Predictive Routing
def cluster_mutations(mutations):
    clusters = {'stable': [], 'mutating': [], 'threat': []}
    for m in mutations:
        if m['type'] == 'mutation':
            clusters['mutating'].append(m)
        elif m['type'] == 'threat':
            clusters['threat'].append(m)
        else:
            clusters['stable'].append(m)
    return clusters

def predict_routing(mutation):
    if CONFIG['panels'][8]['enabled']:
        zone = ai.predict_zone(mutation['size'], mutation['type'])
        if zone == 0:
            return {'x': random.randint(50, 300), 'y': random.randint(50, 150)}
        elif zone == 1:
            return {'x': random.randint(300, 600), 'y': random.randint(100, 200)}
        else:
            return {'x': random.randint(600, 850), 'y': random.randint(200, 300)}
    else:
        return {'x': random.randint(50, 800), 'y': 100}

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
        mutations = snapshot['mutations']
        if CONFIG['panels'][6]['enabled']:
            clusters = cluster_mutations(mutations)
            for state, group in clusters.items():
                for m in group:
                    pos = predict_routing(m) if CONFIG['panels'][7]['enabled'] else {'x': random.randint(50, 800), 'y': 100}
                    self.spawn_glyph(pos['x'], pos['y'], state)
        else:
            for i, m in enumerate(mutations):
                x = 50 + (i * 60)
                y = 100
                state = 'mutating' if m['type'] == 'mutation' else 'stable'
                if m['type'] == 'threat':
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

       # 🧠 Panels
        self.glyph_canvas = GlyphCanvas(self, width=900, height=250)
        self.glyph_canvas.pack()

        self.heatmap = HeatmapPanel(self)
        self.heatmap.pack(pady=10)

        self.timeline = TimelinePanel(self)
        self.timeline.pack(pady=10)

        # 🌀 Start update loop
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

