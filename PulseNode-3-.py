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
import socket
import matplotlib.pyplot as plt
from collections import Counter

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
    for lib in ["numpy", "requests", "psutil", "colorama", "matplotlib"]:
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

# 📊 Entropy Analyzer
def analyze_codex_entropy():
    with open("codex_vault.json", "r") as f:
        data = json.load(f)
    entropy_values = [entry["entropy"] for entry in data]
    plt.figure(figsize=(8, 4))
    plt.plot(entropy_values, label="Entropy", color="#00ffcc")
    plt.title("Symbolic Entropy Over Time")
    plt.xlabel("Pulse Index")
    plt.ylabel("Entropy")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# 🧠 Symbolic Density Map
def show_symbol_density():
    with open("codex_vault.json", "r") as f:
        data = json.load(f)
    symbols = [entry["symbol"] for entry in data]
    counts = Counter(symbols)
    plt.bar(counts.keys(), counts.values(), color="#00ffcc")
    plt.title("Symbolic Density")
    plt.xlabel("Symbol")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

# 🛡️ FallbackRouter: GPU health check
def check_gpu_health():
    load = random.randint(0, 100)
    if load > 80:
        print("[FallbackRouter] GPU overloaded. Rerouting to CPU.")
        return "CPU"
    else:
        print("[FallbackRouter] GPU healthy.")
        return "GPU"

# 🧠 SwarmSyncEmitter (peer-to-peer simulation)
def start_swarm_node(port):
    def handle_client(conn):
        data = conn.recv(1024).decode()
        print(f"[Swarm] Received mutation vote: {data}")
        conn.send(b"Vote acknowledged")
        conn.close()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", port))
    server.listen()
    threading.Thread(target=lambda: server_loop(server)).start()

def server_loop(server):
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()

def emit_mutation_vote(symbol, peer_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", peer_port))
        s.send(symbol.encode())
        response = s.recv(1024).decode()
        print(f"[Swarm] Peer response: {response}")
        s.close()
    except Exception as e:
        print(f"[Swarm] Sync failed: {e}")

# 🎨 Cinematic Pulse Mapping (basic)
def generate_pulse():
    symbol_tag = random.choice(["α", "β", "γ", "δ", "Ω"])
    entropy = round(random.uniform(0.1, 1.0), 3)
    lineage = f"root→{symbol_tag}"
    log_to_codex(symbol_tag, entropy, lineage)
    emit_mutation_vote(symbol_tag, 9090)
    return symbol_tag, entropy, lineage

# 🖥️ GUI: MagicBoxUI Themed Edition
def launch_gui():
    root = tk.Tk()
    root.title("MagicBoxUI - PulseNode vX")
    root.geometry("640x480")
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

    def show_entropy():
        analyze_codex_entropy()

    def show_density():
        show_symbol_density()

    start_btn = tk.Button(root, text="Start PulseNode", font=("Arial", 16), bg="#00ffcc", fg="#000000", command=start_pulse)
    start_btn.pack(pady=10)

    entropy_btn = tk.Button(root, text="Show Entropy Graph", font=("Arial", 14), bg="#4444aa", fg="#ffffff", command=show_entropy)
    entropy_btn.pack(pady=5)

    density_btn = tk.Button(root, text="Show Symbol Density", font=("Arial", 14), bg="#4444aa", fg="#ffffff", command=show_density)
    density_btn.pack(pady=5)

    root.mainloop()

# 🚀 Main Execution
if __name__ == "__main__":
    elevate()
    autoload_libraries()
    start_swarm_node(9090)
    launch_gui()

