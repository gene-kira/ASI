import tkinter as tk
from tkinter import ttk
import threading
import time
import importlib
import sys
import subprocess
import psutil

# 🧙 AutoLoader: Ensures required libraries are present
REQUIRED_LIBS = ['psutil', 'pynvml']

def autoload_libraries():
    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

import pynvml
pynvml.nvmlInit()

# 🧠 RAM Scanner
def scan_system_ram():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "free": mem.available,
        "percent": mem.percent
    }

# 🎮 VRAM Scanner (NVIDIA only)
def scan_vram():
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        total = mem_info.total // (1024**2)
        used = mem_info.used // (1024**2)
        free = mem_info.free // (1024**2)
        percent = round((used / total) * 100, 2)
        return {
            "total": total,
            "used": used,
            "free": free,
            "percent": percent,
            "status": f"{used}MB used of {total}MB ({percent}%)"
        }
    except Exception as e:
        return {
            "total": "N/A",
            "used": "N/A",
            "free": "N/A",
            "percent": 0,
            "status": f"VRAM scan failed: {str(e)}"
        }

# 🕵️ Process Watcher
def get_active_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['memory_percent'] > 1.0:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)

# 🎨 Glyph Renderer
def render_glyph(ram_status, vram_status):
    if ram_status["percent"] > 85 or vram_status["percent"] > 85:
        return "🔥 Shadow Serpent Detected"
    elif ram_status["percent"] > 65 or vram_status["percent"] > 65:
        return "⚠️ Whispering Wraiths"
    else:
        return "🛡️ Memory Guardian Stable"

# 🧙‍♂️ GUI: MagicBox Edition
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 ASI Memory Guard - MagicBox Edition")
        self.root.geometry("600x520")
        self.root.configure(bg="#1e1e2e")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#444", foreground="#fff")
        style.configure("TLabel", font=("Segoe UI", 12), background="#1e1e2e", foreground="#fff")

        self.label = ttk.Label(root, text="ASI Memory Guard is watching...", font=("Segoe UI", 14))
        self.label.pack(pady=10)

        self.result_label = ttk.Label(root, text="", wraplength=550)
        self.result_label.pack(pady=10)

        self.process_label = ttk.Label(root, text="", wraplength=550)
        self.process_label.pack(pady=10)

        self.glyph_label = ttk.Label(root, text="", font=("Segoe UI", 16))
        self.glyph_label.pack(pady=20)

        self.running = True
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def monitor_loop(self):
        while self.running:
            ram_status = scan_system_ram()
            vram_status = scan_vram()
            glyph = render_glyph(ram_status, vram_status)
            processes = get_active_processes()

            result_text = (
                f"🧠 RAM Usage:\n"
                f"Total: {ram_status['total'] // (1024**2)} MB\n"
                f"Used: {ram_status['used'] // (1024**2)} MB\n"
                f"Free: {ram_status['free'] // (1024**2)} MB\n"
                f"Usage: {ram_status['percent']}%\n\n"
                f"🎮 VRAM Usage:\n{vram_status['status']}"
            )

            proc_text = "🕵️ High Memory Processes:\n"
            for proc in processes[:5]:
                proc_text += f"{proc['name']} (PID {proc['pid']}): {proc['memory_percent']:.2f}%\n"

            self.result_label.config(text=result_text)
            self.process_label.config(text=proc_text)
            self.glyph_label.config(text=glyph)

            time.sleep(5)

# 🚀 Launch GUI
def launch_gui():
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: setattr(app, 'running', False) or root.destroy())
    root.mainloop()

if __name__ == "__main__":
    launch_gui()

