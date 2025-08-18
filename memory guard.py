import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import importlib
import sys
import subprocess
import psutil

# 🧙 AutoLoader: Ensures required libraries are present
REQUIRED_LIBS = ['psutil']

def autoload_libraries():
    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

# 🧠 MemorySentinel: RAM scanner stub
def scan_system_ram():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "free": mem.available,
        "percent": mem.percent
    }

# 🎮 VRAM Sentinel stub (placeholder for GPU memory scan)
def scan_vram():
    return {
        "total": "N/A",
        "used": "N/A",
        "free": "N/A",
        "status": "VRAM scan module not yet implemented"
    }

# 🎨 Glyph Renderer: symbolic feedback
def render_glyph(memory_status):
    if memory_status["percent"] > 80:
        return "🔥 Shadow Serpent Detected"
    elif memory_status["percent"] > 60:
        return "⚠️ Whispering Wraiths"
    else:
        return "🛡️ Memory Guardian Stable"

# 🧙‍♂️ GUI: MagicBox Edition
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 ASI Memory Guard - MagicBox Edition")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e2e")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#444", foreground="#fff")
        style.configure("TLabel", font=("Segoe UI", 12), background="#1e1e2e", foreground="#fff")

        self.label = ttk.Label(root, text="Welcome to the ASI Memory Guard")
        self.label.pack(pady=20)

        self.scan_button = ttk.Button(root, text="🧪 Scan Memory", command=self.run_scan)
        self.scan_button.pack(pady=10)

        self.result_label = ttk.Label(root, text="", wraplength=400)
        self.result_label.pack(pady=10)

        self.glyph_label = ttk.Label(root, text="", font=("Segoe UI", 16))
        self.glyph_label.pack(pady=20)

    def run_scan(self):
        self.result_label.config(text="Scanning memory...")
        threading.Thread(target=self.perform_scan).start()

    def perform_scan(self):
        ram_status = scan_system_ram()
        vram_status = scan_vram()
        glyph = render_glyph(ram_status)

        result_text = (
            f"🧠 RAM Usage:\n"
            f"Total: {ram_status['total'] // (1024**2)} MB\n"
            f"Used: {ram_status['used'] // (1024**2)} MB\n"
            f"Free: {ram_status['free'] // (1024**2)} MB\n"
            f"Usage: {ram_status['percent']}%\n\n"
            f"🎮 VRAM Status:\n{vram_status['status']}"
        )

        self.result_label.config(text=result_text)
        self.glyph_label.config(text=glyph)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

