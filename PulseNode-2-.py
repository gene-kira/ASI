import subprocess
import sys
import os
import ctypes
import tkinter as tk
from tkinter import messagebox
import importlib.util
import json
import random
import psutil
import threading
import time

# 🔐 Auto-admin elevation
def elevate():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

# 🔄 Autoloader for required libraries
def autoload_libraries():
    missing = []
    for lib in ["numpy", "requests", "psutil", "colorama"]:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

# 🧬 CodexVault: symbolic memory logger
def log_to_codex(symbol_tag, entropy, lineage):
    vault_path = "codex_vault.json"
    entry = {
        "symbol": symbol_tag,
        "entropy": entropy,
        "lineage": lineage,
        "timestamp": time.time()
    }
    if os.path.exists(vault_path):
        with open(vault_path, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(vault_path, "w") as f:
        json.dump(data, f, indent=2)

# 🧠 SwarmSyncEmitter (simulated)
def emit_swarm_sync(symbol_tag):
    print(f"[SwarmSync] Emitting mutation vote for symbol: {symbol_tag}")
    # Simulate sync delay
    time.sleep(0.5)
    print(f"[SwarmSync] Sync confirmed with 3 nodes")

# 🛡️ FallbackRouter: GPU health check
def check_gpu_health():
    # Simulate GPU load check
    load = random.randint(0, 100)
    if load > 80:
        print("[FallbackRouter] GPU overloaded. Rerouting to CPU.")
        return "CPU"
    else:
        print("[FallbackRouter] GPU healthy.")
        return "GPU"

# 🎨 Cinematic Pulse Mapping (basic)
def generate_pulse():
    symbol_tag = random.choice(["α", "β", "γ", "δ", "Ω"])
    entropy = round(random.uniform(0.1, 1.0), 3)
    lineage = f"root→{symbol_tag}"
    log_to_codex(symbol_tag, entropy, lineage)
    emit_swarm_sync(symbol_tag)
    return symbol_tag, entropy, lineage

# 🖥️ GUI: MagicBoxUI Themed Edition
def launch_gui():
    root = tk.Tk()
    root.title("MagicBoxUI - PulseNode vX")
    root.geometry("600x400")
    root.configure(bg="#1e1e2f")

    title = tk.Label(root, text="🧠 MagicBoxUI Daemon", font=("Arial", 22, "bold"), fg="#00ffcc", bg="#1e1e2f")
    title.pack(pady=20)

    status = tk.Label(root, text="Status: Ready to Pulse", font=("Arial", 14), fg="#ffffff", bg="#1e1e2f")
    status.pack(pady=10)

    pulse_output = tk.Label(root, text="", font=("Arial", 12), fg="#00ffcc", bg="#1e1e2f")
    pulse_output.pack(pady=10)

    def start_pulse():
        status.config(text="Status: Syncing...", fg="#00ffcc")
        route = check_gpu_health()
        symbol, entropy, lineage = generate_pulse()
        pulse_output.config(text=f"Symbol: {symbol} | Entropy: {entropy} | Lineage: {lineage} | Route: {route}")
        status.config(text="Status: Pulse Complete", fg="#00ffcc")

    start_btn = tk.Button(root, text="Start PulseNode", font=("Arial", 16), bg="#00ffcc", fg="#000000", command=start_pulse)
    start_btn.pack(pady=30)

    root.mainloop()

# 🚀 Main Execution
if __name__ == "__main__":
    elevate()
    autoload_libraries()
    launch_gui()

