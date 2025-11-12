#!/usr/bin/env python3
# Codex Unified Launcher — Service + GUI + Preflight + Fallback Repair

import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import Text, Label, Button, END

LOG_FILE = "codex_mutation_log.txt"
SERVICE_NAME = "CodexPurgeShell"

# 🧬 Mutation Log
def log_mutation(event):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {event}\n")
    except Exception as e:
        print(f"Log write failed: {e}")

# 🧪 Preflight Check + Fallback Repair
def preflight_check():
    print("🔧 Codex Preflight: Checking dependencies...\n")
    required_modules = {
        "psutil": "psutil",
        "tkinter": None,
        "pywin32": "pywin32",
        "win32service": "pywin32",
        "win32serviceutil": "pywin32",
        "win32event": "pywin32",
        "servicemanager": "pywin32"
    }
    for module, pip_name in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {module} is installed.")
        except ImportError:
            if pip_name:
                print(f"⚠️ {module} missing. Installing {pip_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                print(f"✅ {module} installed.")
            else:
                print(f"⚠️ {module} not found. tkinter may need manual install on Linux/macOS.")

    try:
        subprocess.run([sys.executable, "-m", "pywin32_postinstall", "-install"], check=True)
        print("✅ pywin32 post-install completed.")
    except Exception as e:
        print(f"⚠️ pywin32 post-install failed: {e}")

    # 🛠️ Verify win32service constants
    try:
        import win32service
        _ = win32service.SERVICE_RUNNING
        print("🎉 win32service constants verified.")
    except Exception as e:
        print(f"❌ win32service verification failed: {e}")
        fallback_repair()

def fallback_repair():
    print("\n🛠️ Fallback Repair Mode Activated")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pywin32"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
        subprocess.run([sys.executable, "-m", "pywin32_postinstall", "-install"], check=True)
        import win32service
        _ = win32service.SERVICE_RUNNING
        print("✅ Repair successful. win32service constants are now available.")
        log_mutation("Fallback repair completed successfully.")
    except Exception as e:
        print(f"❌ Repair failed: {e}")
        log_mutation(f"Fallback repair failed: {e}")

# 🧠 Deepfake Detection (Placeholder)
def detect_deepfake(content):
    log_mutation("Deepfake scan initiated")
    return {"status": "clean", "confidence": 0.98}

# 🌐 Browser Telemetry Purge
def purge_browser_telemetry():
    try:
        import psutil
        browser_tasks = [
            "MicrosoftEdgeUpdateTaskMachineCore",
            "GoogleUpdateTaskMachineUA",
            "MozillaMaintenanceService"
        ]
        for task in browser_tasks:
            subprocess.run(["schtasks", "/Delete", "/TN", task, "/F"], check=True)
            log_mutation(f"Purged scheduled task: {task}")
        browser_processes = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe"]
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in browser_processes:
                log_mutation(f"Browser detected: {proc.info['name']}")
    except Exception as e:
        log_mutation(f"Telemetry purge failed: {e}")

# 🧿 Daemon Pulse
def daemon_loop():
    while True:
        log_mutation("Codex daemon pulse")
        purge_browser_telemetry()
        detect_deepfake("placeholder_content")
        time.sleep(300)

# 🧩 GUI Monitor
class CodexMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Codex Service Monitor")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f0f0f")
        self.build_panels()
        self.refresh_status()
        self.refresh_log()
        self.root.mainloop()

    def build_panels(self):
        Label(self.root, text="Codex Service Monitor", fg="#00ffcc", bg="#0f0f0f", font=("Consolas", 20)).pack(pady=10)
        self.status_label = Label(self.root, text="Checking service status...", fg="#ff0", bg="#0f0f0f", font=("Consolas", 14))
        self.status_label.pack(pady=5)
        Button(self.root, text="Refresh Status", command=self.refresh_status, bg="#222", fg="#fff").pack(pady=5)
        Button(self.root, text="Reload Log", command=self.refresh_log, bg="#222", fg="#fff").pack(pady=5)
        self.log_view = Text(self.root, bg="#111", fg="#0f0", font=("Consolas", 10), wrap="word")
        self.log_view.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_status(self):
        try:
            result = subprocess.run(["sc", "query", SERVICE_NAME], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.status_label.config(text="Codex Service Status: RUNNING", fg="#0f0")
            elif "STOPPED" in result.stdout:
                self.status_label.config(text="Codex Service Status: STOPPED", fg="#f00")
            else:
                self.status_label.config(text="Codex Service Status: UNKNOWN", fg="#ff0")
        except Exception as e:
            self.status_label.config(text=f"Error checking service: {e}", fg="#f00")

    def refresh_log(self):
        self.log_view.delete(1.0, END)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()[-100:]
                for line in lines:
                    self.log_view.insert(END, line)
        else:
            self.log_view.insert(END, "No mutation log found.\n")

# 🌀 Windows Service Wrapper
def define_service():
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager

    class CodexService(win32serviceutil.ServiceFramework):
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = "Codex Purge Shell Daemon"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.running = True

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.running = False
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self):
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, "Codex Purge Shell Daemon started"))
            daemon_loop()

    return CodexService, win32serviceutil

# 🧠 Unified Launcher Entry Point
if __name__ == '__main__':
    preflight_check()
    if len(sys.argv) == 1:
        CodexMonitorGUI()
    else:
        CodexService, win32serviceutil = define_service()
        win32serviceutil.HandleCommandLine(CodexService)

