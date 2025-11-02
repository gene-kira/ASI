# Chameleon Sentinel: Autonomous daemon with GUI, symbolic obfuscation, and manual timer presets
import os
import sys
import time
import threading
import subprocess

# 🔧 Autoloader: Ensures all required libraries are installed
def autoload_libraries():
    required = [
        "watchdog",      # File monitoring
        "cryptography",  # Obfuscation
        "tkinter",       # GUI
        "psutil",        # Resurrection detection
        "pystray",       # Tray icon
        "PIL"            # Image support for GUI
    ]
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

# 🔐 Imports after autoload
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import ttk
import psutil
from PIL import Image
import pystray

# 📁 Paths
SOURCE_DIR = os.path.expandvars(r"%LocalAppData%\Comms\UnistoreDB")
SHADOW_DIR = os.path.join(SOURCE_DIR + "_Shadow")
KEY_PATH = os.path.join(SHADOW_DIR, "chameleon.key")

# 🔑 Obfuscation Key
def load_or_create_key():
    if not os.path.exists(KEY_PATH):
        os.makedirs(SHADOW_DIR, exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return Fernet(key)

cipher = load_or_create_key()

# 🦎 Obfuscation Engine
def obfuscate_file(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        shadow_path = os.path.join(SHADOW_DIR, os.path.basename(path) + ".shadow")
        with open(shadow_path, "wb") as f:
            f.write(encrypted)
    except Exception as e:
        print(f"Obfuscation failed: {e}")

# 🧬 Resurrection Detection
def detect_resurrection():
    for proc in psutil.process_iter(['name']):
        if "Unistore" in proc.info['name']:
            return True
    return False

# 👁️ Watcher Daemon
class ChameleonHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory: return
        obfuscate_file(event.src_path)

def start_watcher():
    observer = Observer()
    observer.schedule(ChameleonHandler(), SOURCE_DIR, recursive=True)
    observer.start()
    return observer

# ⏱️ Manual Timer Controller
class TimerController:
    def __init__(self, interval=5):
        self.interval = interval
        self.running = True

    def set_interval(self, new_interval):
        self.interval = new_interval

    def stop(self):
        self.running = False

    def run(self, callback):
        while self.running:
            time.sleep(self.interval)
            callback()

# 🖥️ GUI Overlay
def launch_gui(timer_controller):
    root = tk.Tk()
    root.title("Chameleon Sentinel")
    root.geometry("400x400")
    root.resizable(False, False)

    status = ttk.Label(root, text="Daemon Active", font=("Consolas", 14))
    status.pack(pady=10)

    log = tk.Text(root, height=10, width=50)
    log.pack()

    def update_log():
        if detect_resurrection():
            log.insert(tk.END, "[!] Resurrection attempt detected\n")
        else:
            log.insert(tk.END, "[✓] All quiet\n")
        log.see(tk.END)

    def on_slider_change(val):
        timer_controller.set_interval(float(val))

    slider_label = ttk.Label(root, text="Check Interval (seconds):")
    slider_label.pack()
    interval_slider = ttk.Scale(root, from_=1, to=86400, orient="horizontal", command=on_slider_change)
    interval_slider.set(timer_controller.interval)
    interval_slider.pack()

    # Preset Buttons
    preset_frame = ttk.Frame(root)
    preset_frame.pack(pady=5)

    def set_preset(seconds):
        timer_controller.set_interval(seconds)
        interval_slider.set(seconds)

    ttk.Button(preset_frame, text="1 Min", command=lambda: set_preset(60)).pack(side="left", padx=5)
    ttk.Button(preset_frame, text="1 Hr", command=lambda: set_preset(3600)).pack(side="left", padx=5)
    ttk.Button(preset_frame, text="1 Day", command=lambda: set_preset(86400)).pack(side="left", padx=5)

    threading.Thread(target=lambda: timer_controller.run(update_log), daemon=True).start()
    root.mainloop()

# 🧿 Tray Icon
def launch_tray():
    image = Image.new("RGB", (64, 64), color=(0, 255, 0))
    icon = pystray.Icon("Chameleon Sentinel", image, "Sentinel Active")
    icon.run()

# 🚀 Main Execution
def main():
    timer_controller = TimerController(interval=5)
    threading.Thread(target=lambda: launch_gui(timer_controller), daemon=True).start()
    threading.Thread(target=launch_tray, daemon=True).start()
    watcher = start_watcher()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        timer_controller.stop()
    watcher.join()

if __name__ == "__main__":
    main()

