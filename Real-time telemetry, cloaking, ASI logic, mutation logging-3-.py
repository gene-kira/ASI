# === VeilMind Nexus — IP Fusion Edition ===
# Author: killer666 + Copilot
# Modules: Real-time IP telemetry, cloaking, ASI logic, GUI feedback
# Status: Clean, modular, ready to evolve

import subprocess
import sys

# === Auto-loader for required libraries ===
required = ['tkinter', 'psutil', 'cryptography', 'requests', 'socket']
for lib in required:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import tkinter as tk
import psutil, socket, requests
from cryptography.fernet import Fernet
import threading, time, random

# === Config ===
SWARM_ID = "VEILMIND-IPFUSION-001"
CLOAK_KEY = Fernet.generate_key()
fernet = Fernet(CLOAK_KEY)
symbolic_memory = {
    "ip_pulse": [],
    "mutations": [],
    "emotions": []
}

# === Real-Time IP Telemetry ===
def get_ip_telemetry():
    local_ip = socket.gethostbyname(socket.gethostname())
    public_ip = requests.get("https://api.ipify.org").text
    connections = psutil.net_connections(kind='inet')
    remote_ips = list(set(conn.raddr.ip for conn in connections if conn.raddr))

    return {
        "Local_IP": local_ip,
        "Public_IP": public_ip,
        "Remote_IPs": remote_ips[:5]  # Limit to top 5 for GUI clarity
    }

# === Cloaking Layer ===
def cloak(data):
    encoded = fernet.encrypt(str(data).encode())
    mutation_id = f"MUT-{random.randint(1000,9999)}"
    symbolic_memory["mutations"].append(mutation_id)
    return encoded, mutation_id

# === ASI Logic Core ===
def asi_think(data):
    logic = {}
    count = len(data.get("Remote_IPs", []))
    emotion = interpret_emotion(count)
    symbolic_memory["emotions"].append(emotion)
    logic["IP_Count"] = {"value": count, "emotion": emotion}
    return logic

def interpret_emotion(val):
    if val > 10: return "⚠️ ALERT"
    elif val > 5: return "🔶 TENSION"
    else: return "🟢 CALM"

# === GUI: MagicBox Edition ===
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 VeilMind Nexus — IP Fusion")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e2f")

        self.title = tk.Label(root, text="VeilMind IP Fusion", font=("Helvetica", 16, "bold"), fg="#00ffff", bg="#1e1e2f")
        self.title.pack(pady=10)

        self.labels = {}
        for label in ["Local_IP", "Public_IP", "Remote_IPs"]:
            lbl = tk.Label(root, text=f"{label}: --", font=("Helvetica", 12), fg="#ffffff", bg="#1e1e2f")
            lbl.pack(anchor="w", padx=10)
            self.labels[label] = lbl

        self.mutation_label = tk.Label(root, text="Mutation ID: --", font=("Helvetica", 10), fg="#ff00ff", bg="#1e1e2f")
        self.mutation_label.pack(pady=5)

        self.emotion_label = tk.Label(root, text="Last Emotion: --", font=("Helvetica", 12), fg="#00ff00", bg="#1e1e2f")
        self.emotion_label.pack(pady=5)

        self.update_loop()

    def update_loop(self):
        telemetry = get_ip_telemetry()
        cloaked, mutation_id = cloak(telemetry)
        logic = asi_think(telemetry)

        self.labels["Local_IP"].config(text=f"Local IP: {telemetry['Local_IP']}")
        self.labels["Public_IP"].config(text=f"Public IP: {telemetry['Public_IP']}")
        self.labels["Remote_IPs"].config(text=f"Remote IPs: {', '.join(telemetry['Remote_IPs'])}")

        self.mutation_label.config(text=f"Mutation ID: {mutation_id}")
        self.emotion_label.config(text=f"Last Emotion: {symbolic_memory['emotions'][-1]}")
        self.root.after(5000, self.update_loop)

# === Launch ===
def launch_magicbox():
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    print(f"[LAUNCH] VeilMind Nexus '{SWARM_ID}' initializing...")
    launch_magicbox()

