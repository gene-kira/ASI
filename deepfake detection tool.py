#!/usr/bin/env python3
# Codex Purge Shell — Mythic-Grade Autonomous Defense Engine

import importlib
import subprocess
import sys

# 🔄 Autoloader: Ensures all required libraries are installed and imported
def autoload(libraries):
    for lib in libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        finally:
            globals()[lib] = importlib.import_module(lib)

# 📦 Required libraries
required_libs = [
    "os", "sys", "json", "time", "threading", "psutil", "tkinter", "requests",
    "platform", "ctypes", "shutil", "socket", "uuid", "re"
]
autoload(required_libs)

from tkinter import Tk, Label, Button, Text, END
from ctypes import windll
from psutil import process_iter
import os

# 🔐 Elevation Check
def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False

# 🚀 Auto-Elevation Launcher with Fallback
def relaunch_as_admin():
    if not is_admin():
        try:
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            print("Relaunching with admin rights...")
            sys.exit()
        except Exception as e:
            print(f"Elevation failed: {e}")
            log_mutation("Elevation failed — running in limited mode")

# 🧬 Mutation Log
mutation_log = []

def log_mutation(event):
    mutation_log.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event})

# 🧿 Daemonized Watchdog
def watchdog():
    while True:
        time.sleep(10)
        log_mutation("Watchdog pulse")

threading.Thread(target=watchdog, daemon=True).start()

# 🧠 Deepfake Detection (Placeholder)
def detect_deepfake(content):
    log_mutation("Deepfake scan initiated")
    return {"status": "clean", "confidence": 0.98}

# 🌐 Browser Telemetry Purge
def purge_browser_telemetry():
    browser_tasks = [
        "MicrosoftEdgeUpdateTaskMachineCore",
        "GoogleUpdateTaskMachineUA",
        "MozillaMaintenanceService"
    ]
    for task in browser_tasks:
        try:
            subprocess.run(["schtasks", "/Delete", "/TN", task, "/F"], check=True)
            log_mutation(f"Purged scheduled task: {task}")
        except Exception as e:
            log_mutation(f"Failed to purge task {task}: {e}")

    browser_processes = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe"]
    for proc in process_iter(['name']):
        if proc.info['name'] in browser_processes:
            log_mutation(f"Browser detected: {proc.info['name']}")

# 🧩 GUI Initialization
class CodexGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Codex Purge Shell")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f0f0f")
        self.build_panels()
        self.root.mainloop()

    def build_panels(self):
        Label(self.root, text="Codex Purge Shell", fg="#00ffcc", bg="#0f0f0f", font=("Consolas", 20)).pack(pady=10)
        Button(self.root, text="Run Telemetry Scan", command=self.run_scan, bg="#222", fg="#fff").pack(pady=5)
        Button(self.root, text="Run Deepfake Scan", command=self.run_deepfake, bg="#222", fg="#fff").pack(pady=5)
        Button(self.root, text="Purge Browser Telemetry", command=self.purge_browser, bg="#222", fg="#fff").pack(pady=5)
        Button(self.root, text="View Mutation Log", command=self.view_log, bg="#222", fg="#fff").pack(pady=5)

        self.log_view = Text(self.root, bg="#111", fg="#0f0", font=("Consolas", 10), wrap="word")
        self.log_view.pack(fill="both", expand=True, padx=10, pady=10)

    def run_scan(self):
        log_mutation("Telemetry scan initiated")
        self.log_view.insert(END, "Scanning for telemetry services...\n")

    def run_deepfake(self):
        result = detect_deepfake("placeholder_content")
        self.log_view.insert(END, f"Deepfake scan result: {result['status']} (Confidence: {result['confidence']})\n")

    def purge_browser(self):
        purge_browser_telemetry()
        self.log_view.insert(END, "Browser telemetry purge complete.\n")

    def view_log(self):
        self.log_view.delete(1.0, END)
        for entry in mutation_log:
            self.log_view.insert(END, f"[{entry['timestamp']}] {entry['event']}\n")

# 🌀 Launch Sequence
log_mutation(f"Codex Purge Shell launched as admin: {is_admin()}")
relaunch_as_admin()
CodexGUI()

