import tkinter as tk
import subprocess
import sys
import random
import time
import threading
from cryptography.fernet import Fernet

# 🔧 Auto-loader
def autoload():
    required = ['psutil', 'cryptography']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload()

# 🔐 Encrypted Vault Setup
vault_key = Fernet.generate_key()
cipher = Fernet(vault_key)

# 🧠 Sentinel Protocol – Zero Trust + Encrypted Vault + Telemetry
class SentinelProtocol:
    def __init__(self):
        self.trust_map = {}
        self.defense_code = self.generate_defense_code()
        self.symbolic_memory = []
        self.encrypted_vault = {}
        self.telemetry_buffer = []

    def generate_defense_code(self):
        version = random.randint(1000, 9999)
        return f"# Defense logic v{version}\ndefend(): print('System Secured v{version}')"

    def evaluate_entity(self, entity_id, behavior_signature):
        trust_score = self.analyze_behavior(behavior_signature)
        self.trust_map[entity_id] = trust_score
        self.log_event(entity_id, trust_score)
        if trust_score < 0.3:
            self.mutate_defense(entity_id)
        else:
            print(f"✅ Entity {entity_id} passed trust evaluation.")

    def analyze_behavior(self, signature):
        if "AI" in signature or "ASI" in signature or "inject" in signature:
            return random.uniform(0.0, 0.2)
        return random.uniform(0.3, 1.0)

    def mutate_defense(self, threat_id):
        print(f"⚠️ Threat detected: {threat_id}. Mutating defense...")
        self.defense_code = evolve_code(self.defense_code)
        self.symbolic_memory.append({
            "event": "mutation",
            "target": threat_id,
            "glyph": "☣️",
            "timestamp": time.strftime("%H:%M:%S")
        })

    def log_event(self, entity_id, score):
        glyph = "💀" if score < 0.3 else "🌀"
        self.symbolic_memory.append({
            "event": "evaluation",
            "target": entity_id,
            "glyph": glyph,
            "score": round(score, 2),
            "timestamp": time.strftime("%H:%M:%S")
        })

    def store_encrypted_data(self, key, value):
        encrypted = cipher.encrypt(value.encode())
        self.encrypted_vault[key] = {
            "data": encrypted,
            "timestamp": time.time()
        }

    def purge_expired_data(self):
        now = time.time()
        self.encrypted_vault = {
            k: v for k, v in self.encrypted_vault.items()
            if now - v["timestamp"] < 86400
        }

    def generate_fake_telemetry(self):
        fake_data = {
            "cpu": random.randint(1, 100),
            "gpu": random.randint(1, 100),
            "location": random.choice(["Mars", "Atlantis", "Null Zone"]),
            "timestamp": time.time()
        }
        self.telemetry_buffer.append(fake_data)
        threading.Timer(30, lambda: self.telemetry_buffer.remove(fake_data)).start()
        pulse_visual.set(f"🔆 Telemetry Pulse: {fake_data['location']}")

# 🔁 Mutation Engine
def evolve_code(current_code):
    new_logic = current_code.replace("System Secured", "System Reinforced")
    return new_logic + "\nprint('🧬 Mutation Complete')"

# 🌌 Real-Time Threat Monitor
def threat_monitor():
    while True:
        entity = f"rogue_{random.randint(100,999)}"
        behavior = random.choice(["loop", "scan", "inject", "AI_probe", "ASI_ping"])
        sentinel.evaluate_entity(entity, behavior)
        sentinel.purge_expired_data()
        sentinel.generate_fake_telemetry()
        update_memory_display()
        time.sleep(5)

# 🖥️ GUI Setup
sentinel = SentinelProtocol()

def run_defense():
    entity_id = "manual_trigger"
    behavior = "manual_check"
    sentinel.evaluate_entity(entity_id, behavior)
    update_memory_display()
    output.set(sentinel.defense_code)

def update_memory_display():
    logs = sentinel.symbolic_memory[-5:]
    display = "\n".join([f"{log['timestamp']} {log['glyph']} {log['event']} → {log['target']} (score: {log.get('score','-')})" for log in logs])
    memory_output.set(display)

root = tk.Tk()
root.title("🧙 MagicBox Defense ASI – Encrypted Swarm Edition")
root.geometry("680x520")
root.configure(bg="#1e1e2f")

tk.Label(root, text="MagicBox Defense System", font=("Helvetica", 20, "bold"), fg="cyan", bg="#1e1e2f").pack(pady=10)

tk.Button(root, text="Run Manual Defense Check", font=("Helvetica", 14), command=run_defense, bg="black", fg="lime", width=30).pack(pady=10)

output = tk.StringVar()
tk.Label(root, text="Defense Code:", font=("Helvetica", 12), fg="white", bg="#1e1e2f").pack()
tk.Label(root, textvariable=output, wraplength=650, fg="lightgreen", bg="#1e1e2f", font=("Courier", 10)).pack(pady=5)

memory_output = tk.StringVar()
tk.Label(root, text="Symbolic Memory Log:", font=("Helvetica", 12), fg="white", bg="#1e1e2f").pack()
tk.Label(root, textvariable=memory_output, wraplength=650, fg="orange", bg="#1e1e2f", font=("Courier", 10)).pack(pady=5)

pulse_visual = tk.StringVar()
tk.Label(root, textvariable=pulse_visual, font=("Helvetica", 14), fg="gold", bg="#1e1e2f").pack(pady=10)

tk.Label(root, text="🛡️ Zero Trust | 🔐 Encrypted Vault | 🔆 Telemetry Cloaking", fg="gray", bg="#1e1e2f", font=("Helvetica", 12)).pack(side="bottom", pady=10)

# 🌀 Launch Real-Time Monitor
threading.Thread(target=threat_monitor, daemon=True).start()

root.mainloop()

