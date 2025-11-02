import subprocess
import sys

# === AUTOLOADER: External Library Resurrection ===
EXTERNAL_LIBS = ["psutil", "pywin32"]

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[Autoloader] Installed: {package}")
    except Exception as e:
        print(f"[Autoloader] Failed to install {package}: {e}")

def autoload_libraries():
    for lib in EXTERNAL_LIBS:
        try:
            __import__(lib)
        except ImportError:
            install_package(lib)

autoload_libraries()

# === CORE IMPORTS ===
import os
import time
import winreg
import ctypes
import hashlib
import json
import threading
from datetime import datetime
import tkinter as tk

# === CONFIGURATION ===
WATCHED_KEYS = {
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection": {
        "AllowTelemetry": 0,
        "MaxTelemetryAllowed": 0
    },
    r"SYSTEM\CurrentControlSet\Services\DiagTrack": {
        "Start": 4
    }
}

SNAPSHOT_FILE = "codex_registry_snapshot.json"
LOG_FILE = "codex_mutation_log.txt"
PIPE_NAME = r"\\.\pipe\CodexPurgeGUI"

# === REGISTRY UTILITIES ===
def get_reg_value(hive, path, name):
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except FileNotFoundError:
        return None

def set_reg_value(hive, path, name, value, reg_type=winreg.REG_DWORD):
    try:
        with winreg.CreateKey(hive, path) as key:
            winreg.SetValueEx(key, name, 0, reg_type, value)
    except Exception as e:
        log_event("ERROR", f"Failed to set {path}\\{name}: {e}")

# === LOGGING + GUI BROADCAST ===
def log_event(event_type, message):
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] [{event_type}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")
    broadcast_to_gui(entry)

def broadcast_to_gui(message):
    try:
        with open(PIPE_NAME, "w") as pipe:
            pipe.write(message + "\n")
    except Exception:
        pass  # GUI not listening

# === SNAPSHOT + RESTORE ===
def take_snapshot():
    snapshot = {}
    for path, values in WATCHED_KEYS.items():
        hive = winreg.HKEY_LOCAL_MACHINE if path.startswith("SYSTEM") else winreg.HKEY_CURRENT_USER
        snapshot[path] = {}
        for name in values:
            snapshot[path][name] = get_reg_value(hive, path, name)
    return snapshot

def save_snapshot(snapshot):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f)

def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r") as f:
        return json.load(f)

def restore_snapshot(snapshot):
    for path, values in snapshot.items():
        hive = winreg.HKEY_LOCAL_MACHINE if path.startswith("SYSTEM") else winreg.HKEY_CURRENT_USER
        for name, value in values.items():
            set_reg_value(hive, path, name, value)

def hash_snapshot(snapshot):
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()

# === WATCHDOG THREAD ===
def watchdog_loop():
    last_snapshot = load_snapshot()
    last_hash = hash_snapshot(last_snapshot)

    while True:
        current = take_snapshot()
        current_hash = hash_snapshot(current)

        if current_hash != last_hash:
            log_event("MUTATION", "Registry mutation detected")
            restore_snapshot(last_snapshot)
            log_event("RESURRECTION", "Settings restored from snapshot")
        else:
            log_event("HEARTBEAT", "No mutation detected")

        time.sleep(10)

# === ELEVATION CHECK ===
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

# === GUI OVERLAY ===
class CodexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Codex Purge Sentinel")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e1e")

        self.status_label = tk.Label(root, text="Daemon Status: 🔄 Checking...", fg="white", bg="#1e1e1e", font=("Consolas", 14))
        self.status_label.pack(pady=10)

        self.log_box = tk.Text(root, bg="#2e2e2e", fg="#00ff00", font=("Consolas", 12), wrap="word")
        self.log_box.pack(expand=True, fill="both", padx=10, pady=10)

        self.start_pipe_listener()
        self.start_heartbeat_check()

    def start_pipe_listener(self):
        def listen():
            if not os.path.exists(PIPE_NAME):
                try:
                    os.mkfifo(PIPE_NAME)
                except:
                    pass
            while True:
                try:
                    with open(PIPE_NAME, "r") as pipe:
                        for line in pipe:
                            self.log_box.insert(tk.END, line)
                            self.log_box.see(tk.END)
                except Exception:
                    time.sleep(2)
        threading.Thread(target=listen, daemon=True).start()

    def start_heartbeat_check(self):
        def check():
            while True:
                time.sleep(15)
                self.status_label.config(text="Daemon Status: ✅ Running")
        threading.Thread(target=check, daemon=True).start()

# === MAIN ENTRY ===
def main():
    if not is_admin():
        relaunch_as_admin()
        return

    log_event("INIT", "Codex Purge Daemon initialized")
    snapshot = take_snapshot()
    save_snapshot(snapshot)
    threading.Thread(target=watchdog_loop, daemon=True).start()

    root = tk.Tk()
    app = CodexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

