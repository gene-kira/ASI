import subprocess
import sys
import importlib.util
import os
import json
import time
import socket
import threading
import cupy as cp
import matplotlib.pyplot as plt
from collections import Counter
import tkinter as tk

# 🔄 Autoloader
def autoload_libraries():
    required = ["cupy", "matplotlib"]
    missing = [lib for lib in required if importlib.util.find_spec(lib) is None]
    if missing:
        print(f"[Autoloader] Missing: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("[Autoloader] Installed missing libraries.")
        except Exception as e:
            print(f"[Autoloader] Failed: {e}")
    else:
        print("[Autoloader] All libraries present.")

# 🧬 DLL Path Registration (Windows + Python ≥ 3.8)
def register_cuda_dll_path():
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        cuda_path = os.environ.get("CUDA_PATH")
        if cuda_path:
            dll_dir = os.path.join(cuda_path, "bin")
            try:
                os.add_dll_directory(dll_dir)
                print(f"[DLL] Registered CUDA DLL path: {dll_dir}")
            except Exception as e:
                print(f"[DLL] Failed to register CUDA path: {e}")
        else:
            print("[DLL] CUDA_PATH not set. Skipping DLL registration.")

# 🧠 GPU math ops with CuPy
def run_gpu_ops():
    N = 1000
    a = cp.random.rand(N)
    b = cp.random.rand(N)
    out = a * b
    return out

# 🔬 Entropy from GPU array
def compute_entropy(arr):
    hist, _ = cp.histogram(arr, bins=10, density=True)
    hist = hist[hist > 0]
    entropy = -cp.sum(hist * cp.log2(hist))
    return round(float(entropy), 3)

# 🧬 CodexVault logger
def log_to_codex(symbol, entropy, lineage):
    entry = {
        "symbol": symbol,
        "entropy": entropy,
        "lineage": lineage,
        "timestamp": time.time()
    }
    vault = "codex_vault.json"
    try:
        data = json.load(open(vault)) if os.path.exists(vault) else []
        data.append(entry)
        json.dump(data, open(vault, "w"), indent=2)
    except Exception as e:
        print(f"[Vault] Error: {e}")

# 🧠 Swarm sync
def start_swarm_node(port):
    def handle_client(conn):
        try:
            data = conn.recv(1024).decode()
            print(f"[Swarm] Received vote: {data}")
            conn.send(b"Vote acknowledged")
        except:
            pass
        finally:
            conn.close()

    def server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", port))
        server.listen()
        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

    threading.Thread(target=server_loop, daemon=True).start()

def emit_vote(symbol, port):
    payload = json.dumps({"symbol": symbol, "timestamp": time.time()}).encode()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", port))
        s.send(payload)
        print(f"[Swarm] Vote sent: {symbol}")
        s.close()
    except Exception as e:
        print(f"[Swarm] Failed: {e}")

# 🎨 Pulse generator
def generate_pulse():
    result = run_gpu_ops()
    entropy = compute_entropy(result)
    symbol = f"Σ{round(entropy * 100)}"
    lineage = f"root→{symbol}"
    log_to_codex(symbol, entropy, lineage)
    emit_vote(symbol, 9090)
    return symbol, entropy, lineage

# 📊 Visualization
def show_entropy():
    try:
        data = json.load(open("codex_vault.json"))
        values = [entry["entropy"] for entry in data]
        plt.plot(values, color="#00ffcc")
        plt.title("Entropy Over Time")
        plt.xlabel("Pulse Index")
        plt.ylabel("Entropy")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except:
        print("[Graph] Failed")

def show_density():
    try:
        data = json.load(open("codex_vault.json"))
        symbols = [entry["symbol"] for entry in data]
        counts = Counter(symbols)
        plt.bar(counts.keys(), counts.values(), color="#00ffcc")
        plt.title("Symbolic Density")
        plt.xlabel("Symbol")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()
    except:
        print("[Graph] Failed")

# 🖥️ GUI
def launch_gui():
    root = tk.Tk()
    root.title("MagicBoxUI - CuPy Edition")
    root.geometry("640x480")
    root.configure(bg="#1e1e2f")

    title = tk.Label(root, text="🧠 MagicBoxUI Daemon", font=("Arial", 22, "bold"), fg="#00ffcc", bg="#1e1e2f")
    title.pack(pady=20)

    status = tk.Label(root, text="Status: Ready", font=("Arial", 14), fg="#ffffff", bg="#1e1e2f")
    status.pack(pady=10)

    output = tk.Label(root, text="", font=("Arial", 12), fg="#00ffcc", bg="#1e1e2f")
    output.pack(pady=10)

    def pulse():
        status.config(text="Status: Processing...", fg="#00ffcc")
        symbol, entropy, lineage = generate_pulse()
        output.config(text=f"Symbol: {symbol} | Entropy: {entropy} | Lineage: {lineage}")
        status.config(text="Status: Complete", fg="#00ffcc")

    tk.Button(root, text="Start Pulse", font=("Arial", 16), bg="#00ffcc", fg="#000000", command=pulse).pack(pady=10)
    tk.Button(root, text="Show Entropy", font=("Arial", 14), bg="#4444aa", fg="#ffffff", command=show_entropy).pack(pady=5)
    tk.Button(root, text="Show Density", font=("Arial", 14), bg="#4444aa", fg="#ffffff", command=show_density).pack(pady=5)

    root.mainloop()

# 🚀 Main
if __name__ == "__main__":
    autoload_libraries()
    register_cuda_dll_path()
    start_swarm_node(9090)
    launch_gui()

