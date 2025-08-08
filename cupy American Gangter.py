# MagicBox_MythicFinalEdition.py

import subprocess, sys

# 🧰 Auto-install required libraries
def autoload_libs():
    required = ['psutil', 'cupy']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libs()

import psutil
import cupy as cp
import tkinter as tk
from tkinter import ttk
import threading, time, random

# 🧬 Self-Rewriting Agent
agent_weights = cp.array([0.6, -0.8, -0.3])
mutation_log = []

def gpu_trust_score(entity_vector):
    trust_vector = cp.array(entity_vector)
    score = cp.dot(trust_vector, agent_weights)
    return float(score.get())

def mutate_agent(entity_id, score):
    global agent_weights
    mutation_log.append(f"{entity_id} → TrustScore: {score:.2f}")
    if score < 0.3:
        agent_weights += cp.array([random.uniform(-0.05, 0.05) for _ in range(3)])
        log_event(f"🧬 Agent mutated: new weights = {agent_weights.get()}")

# 🔐 Glyph-Based Encryption
glyph_map = {
    'a': 'ᚨ', 'e': 'ᛖ', 'i': 'ᛁ', 'o': 'ᛟ', 'u': 'ᚢ',
    'r': 'ᚱ', 'g': 'ᚷ', 'h': 'ᚺ', 's': 'ᛋ', 't': 'ᛏ',
    'n': 'ᚾ', 'l': 'ᛚ', 'd': 'ᛞ', 'm': 'ᛗ', 'b': 'ᛒ',
    'c': 'ᚲ', 'y': 'ᛃ', 'z': 'ᛉ'
}

def glyph_encrypt(text):
    return ''.join(glyph_map.get(ch.lower(), ch) for ch in text)

# 🎥 Particle FX
def trigger_fx(color):
    for _ in range(20):
        x, y = random.randint(50, 650), random.randint(50, 450)
        size = random.randint(5, 15)
        fx = canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
        root.after(300, lambda fx=fx: canvas.delete(fx))

# 🕵️ Threat Detection
def get_live_threat_event():
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        name = proc.info['name'].lower()
        if any(term in name for term in ["rogue", "hack", "mal", "spy", "steal"]):
            return {
                "id": f"proc-{proc.info['pid']}",
                "type": "rogue",
                "source": proc.info['name'],
                "behavior": "suspicious",
                "payload": {
                    "id": f"data-{proc.info['pid']}",
                    "type": "personal",
                    "content": glyph_encrypt(f"user={proc.info['username']}"),
                    "channel": "backdoor"
                }
            }
    return None

# 🧹 Purge Logic
def purge_entity(entity):
    log_event(f"⚠️ PURGE INITIATED: {entity['source']}")
    trigger_fx("red")
    try:
        pid = int(entity['id'].split('-')[-1])
        psutil.Process(pid).terminate()
        log_event(f"✅ Terminated {entity['source']}")
    except Exception as e:
        log_event(f"❌ Purge failed: {e}")

# 🧪 Entity Verifier
def verify_entity_gpu(entity):
    vector = [1, 1 if entity["type"] == "rogue" else 0, 1 if entity.get("behavior") == "suspicious" else 0]
    trust_score = gpu_trust_score(vector)
    mutate_agent(entity["id"], trust_score)
    if trust_score < 0.5:
        purge_entity(entity)
    else:
        log_event(f"🧿 Verified: {entity['id']} (Trust: {trust_score:.2f})")
        trigger_fx("blue")

# 🕸️ Swarm Daemon
def swarm_daemon():
    while True:
        entity = get_live_threat_event()
        if entity:
            verify_entity_gpu(entity)
        time.sleep(3)

# 📜 Event Logger
def log_event(msg):
    gui_log.insert(tk.END, msg + "\n")
    gui_log.see(tk.END)

# 🎨 GUI Setup
root = tk.Tk()
root.title("🧙 MagicBox: Mythic Final Edition")
root.geometry("700x550")
root.configure(bg="#1e1e2e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 14), foreground="#ffffff", background="#5f5fff")
style.configure("TLabel", font=("Segoe UI", 16), foreground="#ffffff", background="#1e1e2e")

ttk.Label(root, text="🛡️ Mythic Defense Engine", background="#1e1e2e", foreground="#ffffff").pack(pady=10)

canvas = tk.Canvas(root, width=700, height=100, bg="#1e1e2e", highlightthickness=0)
canvas.pack()

gui_log = tk.Text(root, height=18, bg="#2e2e3e", fg="#00ffcc", font=("Consolas", 12))
gui_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def start_magicbox():
    log_event("✨ MagicBox activated. Swarm daemons online...")
    threading.Thread(target=swarm_daemon, daemon=True).start()

ttk.Button(root, text="🧙‍♂️ Start MagicBox", command=start_magicbox).pack(pady=10)

# 🧠 Auto-start
start_magicbox()

root.mainloop()

