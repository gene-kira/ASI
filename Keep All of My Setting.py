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
GUI_PIPE = r"\\.\pipe\CodexPurgeGUI"

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
        with open(GUI_PIPE, "w") as pipe:
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

# === MAIN ENTRY ===
def main():
    if not is_admin():
        relaunch_as_admin()
        return

    log_event("INIT", "Codex Purge Daemon initialized")
    snapshot = take_snapshot()
    save_snapshot(snapshot)
    threading.Thread(target=watchdog_loop, daemon=True).start()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()

