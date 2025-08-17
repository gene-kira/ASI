# 🔮 MagicBox Memory Dashboard (Memory Bank Edition)
import os, sys, time, subprocess, random

# 🧰 Auto-loader
def autoload():
    required = ['psutil', 'tkinter', 'PIL', 'cryptography', 'sklearn']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload()

# 🧠 Imports
import psutil
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from sklearn.tree import DecisionTreeClassifier

# ✅ All modules auto-enabled
CONFIG = {
    'glyphGrid': True,
    'heatmapOverlay': True,
    'trailRenderer': True,
    'mutationTimeline': True,
    'threatSim': True,
    'vaultSync': True,
    'swarmClustering': True,
    'predictiveRouting': True,
    'aiRouting': True,
    'memoryBanks': True
}

# 🔐 VaultSync
class VaultSync:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

vault = VaultSync()

# 🧠 AI Predictor
class AIPredictor:
    def __init__(self):
        self.model = DecisionTreeClassifier()
        self.train()

    def train(self):
        X = [[4096, 0], [2048, 1], [1024, 2], [8192, 0], [512, 2]]
        y = [0, 1, 2, 0, 2]
        self.model.fit(X, y)

    def predict_zone(self, size, type_):
        type_code = {'allocation': 0, 'mutation': 1, 'threat': 2}.get(type_, 0)
        return self.model.predict([[size, type_code]])[0]

ai = AIPredictor()

# 🧠 Memory Snapshot
def get_memory_snapshot():
    ram = psutil.virtual_memory()
    ram_used = ram.used // (1024 * 1024)
    ram_total = ram.total // (1024 * 1024)
    vram_total = 8192
    vram_used = 2048 + max(0, ram_used - ram_total)

    mutations = [
        {'address': 0xDEADBEEF, 'size': 4096, 'timestamp': time.time(), 'type': 'allocation'},
        {'address': 0xFEEDBEEF, 'size': 2048, 'timestamp': time.time(), 'type': 'mutation'}
    ]
    if CONFIG['threatSim']:
        mutations.append({'address': 0xBADF00D, 'size': 1024, 'timestamp': time.time(), 'type': 'threat'})
    return {
        'ram_used': ram_used,
        'ram_total': ram_total,
        'vram_used': vram_used,
        'vram_total': vram_total,
        'mutations': mutations
    }

# 🧠 Clustering + Routing
def cluster_mutations(mutations):
    clusters = {'allocation': [], 'mutation': [], 'threat': []}
    for m in mutations:
        clusters[m['type']].append(m)
    return clusters

def predict_routing(mutation):
    zone = ai.predict_zone(mutation['size'], mutation['type'])
    if zone == 0:
        return {'x': random.randint(50, 300), 'y': random.randint(50, 150)}
    elif zone == 1:
        return {'x': random.randint(300, 600), 'y': random.randint(100, 200)}
    else:
        return {'x': random.randint(600, 850), 'y': random.randint(200, 300)}

# 🎨 Glyph Renderer
class GlyphCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='black', **kwargs)

    def update_glyphs(self, snapshot):
        self.delete("all")
        self.draw_memory_banks(snapshot)
        clusters = cluster_mutations(snapshot['mutations'])
        for state, group in clusters.items():
            for m in group:
                pos = predict_routing(m)
                self.spawn_glyph(pos['x'], pos['y'], state, m['address'])

    def spawn_glyph(self, x, y, state, address):
        color = {'allocation': '#00ff00', 'mutation': '#0000ff', 'threat': '#ff0000'}.get(state, '#ffffff')
        radius = 10
        self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        self.create_line(x, y, x, y+20, fill=color)
        self.create_text(x, y+25, text=hex(address)[-6:], fill='white', font=("Arial", 8))

    def draw_memory_banks(self, snapshot):
        if CONFIG['memoryBanks']:
            self.create_text(100, 20, text=f"System RAM [{snapshot['ram_used']} / {snapshot['ram_total']} MB]", fill='white', font=("Arial", 10))
            self.create_text(700, 20, text=f"VRAM [{snapshot['vram_used']} / {snapshot['vram_total']} MB]", fill='white', font=("Arial", 10))
            self.create_rectangle(50, 30, 350, 40, outline='green')
            self.create_rectangle(650, 30, 850, 40, outline='red')

# 🖼️ Heatmap Panel
class HeatmapPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='black')
        self.label = tk.Label(self, text="Memory Heatmap", fg='white', bg='black')
        self.label.pack()
        self.bar = ttk.Progressbar(self, orient='horizontal', length=300, mode='determinate')
        self.bar.pack()
        self.vram_label = tk.Label(self, text="", fg='white', bg='black')
        self.vram_label.pack()

    def update_heatmap(self, snapshot):
        percent = int((snapshot['ram_used'] / snapshot['ram_total']) * 100)
        self.bar['value'] = percent
        self.label.config(text=f"RAM Usage: {percent}%")
        overspill = max(0, snapshot['ram_used'] - snapshot['ram_total'])
        self.vram_label.config(text=f"VRAM Overspill: {overspill} MB | VRAM Used: {snapshot['vram_used']} MB")

# 🌀 Timeline Panel
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
            line = vault.encrypt(line) if CONFIG['vaultSync'] else line
            self.log.insert(tk.END, line + "\n")

# 🧙 MagicBox GUI
class MagicBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧙 MagicBox Memory Dashboard")
        self.geometry("1000x750")
        self.configure(bg='black')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", foreground='green', background='green')

        self.glyph_canvas = GlyphCanvas(self, width=950, height=250)
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
        self.after(1000, self.update_loop)

# 🚀 Launch
if __name__ == "__main__":
    MagicBoxApp().mainloop()

