# MagicBox Daemon GUI - Old Guy Friendly Edition
import subprocess
import sys

# 🧙 Autoloader: Install missing libraries
def autoload():
    try:
        import tkinter
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import tkinter

autoload()

import tkinter as tk
from tkinter import ttk
import requests, hashlib, uuid
from datetime import datetime

# 🧠 Codex Vault
codex_vault = []

# 🧬 Ingest Logic
def ingest_telemetry():
    sources = {
        "Sensor Alpha": "http://localhost:5000/alpha",
        "Sensor Beta": "http://localhost:5000/beta"
    }
    for name, url in sources.items():
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            data = response.text
            hash_digest = hashlib.sha256(data.encode()).hexdigest()
            entry = {
                "id": str(uuid.uuid4()),
                "source": name,
                "timestamp": datetime.utcnow().isoformat(),
                "hash": hash_digest,
                "status": "active"
            }
            codex_vault.append(entry)
            update_codex_display()
        except Exception as e:
            log_output(f"❌ Failed to ingest from {name}: {e}")

# 🖥️ GUI Setup
root = tk.Tk()
root.title("MagicBox Daemon")
root.geometry("800x600")
root.configure(bg="#1c1c2e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 14), padding=10)
style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")

# 🔘 One-Click Ingest Button
def start_ingest():
    log_output("🚀 Ingesting telemetry...")
    ingest_telemetry()

ingest_button = ttk.Button(root, text="Start Telemetry Ingest", command=start_ingest)
ingest_button.pack(pady=20)

# 📜 Codex Vault Display
codex_frame = tk.Frame(root, bg="#1c1c2e")
codex_frame.pack(fill="both", expand=True)

codex_list = tk.Listbox(codex_frame, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
codex_list.pack(fill="both", expand=True, padx=10, pady=10)

def update_codex_display():
    codex_list.delete(0, tk.END)
    for entry in codex_vault[-20:]:
        codex_list.insert(tk.END, f"{entry['timestamp']} | {entry['source']} | {entry['status']}")

# 🧾 Log Output
log_frame = tk.Frame(root, bg="#1c1c2e")
log_frame.pack(fill="x")

log_label = tk.Label(log_frame, text="System Log:", font=("Arial", 12), bg="#1c1c2e", fg="white")
log_label.pack(anchor="w", padx=10)

log_text = tk.Text(log_frame, height=5, bg="#2e2e3e", fg="white", font=("Courier", 10))
log_text.pack(fill="x", padx=10, pady=5)

def log_output(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# 🧙 Launch GUI
log_output("🧿 MagicBox Daemon Ready")
root.mainloop()

