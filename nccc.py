import tkinter as tk
from tkinter import ttk
import threading
import random
import time
import socket
import uuid

class MagicBoxCloakNode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧙‍♂️ MagicBox Cloak Node")
        self.root.geometry("900x700")  # ✅ Wider window to fit full list

        self.status_label = tk.Label(self.root, text="Initializing...", font=("Consolas", 12), fg="white", bg="black")
        self.status_label.pack(pady=10)

        self.ip_list = tk.Listbox(self.root, height=10, width=110, font=("Consolas", 10))  # ✅ Wider listbox + monospace font
        self.ip_list.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=800, mode="determinate")
        self.progress.pack(pady=10)

        self.swarm_canvas = tk.Canvas(self.root, width=800, height=300, bg="black")
        self.swarm_canvas.pack(pady=10)

        self.vault_label = tk.Label(self.root, text="Vault Status: 🔒 Sealed", font=("Consolas", 12), fg="cyan", bg="black")
        self.vault_label.pack(pady=10)

        self.telemetry_label = tk.Label(self.root, text="Fake Telemetry: Injecting...", font=("Consolas", 10), fg="magenta", bg="black")
        self.telemetry_label.pack(pady=5)

        self.mutation_trail = []
        self.swarm_nodes = []

        self.start_threads()
        self.root.mainloop()

    def start_threads(self):
        threading.Thread(target=self.simulate_ip_mutation, daemon=True).start()
        threading.Thread(target=self.simulate_progress, daemon=True).start()
        threading.Thread(target=self.animate_swarm, daemon=True).start()
        threading.Thread(target=self.vault_cycle, daemon=True).start()
        threading.Thread(target=self.inject_fake_telemetry, daemon=True).start()
        threading.Thread(target=self.parallel_threat_scan, daemon=True).start()

    def simulate_ip_mutation(self):
        while True:
            mutated_ip = f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
            geo = random.choice(['🌍 Earth', '🪐 Mars', '🌑 Moon', '🌌 Andromeda'])
            entry = f"🌀 IP: {mutated_ip} | MAC: {mac} | GeoIP: {geo} | Vault: {'Ephemeral'}"
            self.ip_list.insert(0, entry)
            if self.ip_list.size() > 10:
                self.ip_list.delete(10)
            self.status_label.config(text=f"Mutating → {mutated_ip}")
            self.mutation_trail.append(mutated_ip)
            time.sleep(2)

    def simulate_progress(self):
        while True:
            for i in range(101):
                self.progress["value"] = i
                time.sleep(0.03)
            for i in range(100, -1, -1):
                self.progress["value"] = i
                time.sleep(0.03)

    def animate_swarm(self):
        for _ in range(20):
            x, y = random.randint(0, 790), random.randint(0, 290)
            node = self.swarm_canvas.create_oval(x, y, x+10, y+10, fill=random.choice(["cyan", "lime", "magenta"]))
            self.swarm_nodes.append(node)

        while True:
            for node in self.swarm_nodes:
                dx, dy = random.randint(-3, 3), random.randint(-3, 3)
                self.swarm_canvas.move(node, dx, dy)
            self.swarm_canvas.update()
            time.sleep(0.1)

    def vault_cycle(self):
        while True:
            self.vault_label.config(text="Vault Status: 🔓 Rebirthing...", fg="orange")
            time.sleep(3)
            self.vault_label.config(text="Vault Status: 🔒 Sealed", fg="cyan")
            time.sleep(7)

    def inject_fake_telemetry(self):
        while True:
            hostname = socket.gethostname()
            fake_payload = {
                "node": hostname,
                "status": random.choice(["🟢 OK", "🟡 Latency", "🔴 Breach"]),
                "entropy": round(random.uniform(0.1, 0.99), 2),
                "uuid": str(uuid.uuid4())[:8]
            }
            text = f"Fake Telemetry → Node: {fake_payload['node']} | Status: {fake_payload['status']} | Entropy: {fake_payload['entropy']} | UUID: {fake_payload['uuid']}"
            self.telemetry_label.config(text=text)
            time.sleep(4)

    def parallel_threat_scan(self):
        while True:
            threading.Thread(target=self.scan_for_threats, daemon=True).start()
            time.sleep(5)

    def scan_for_threats(self):
        threat = random.choice(["None", "Packet anomaly", "MAC spoof", "GeoIP mismatch", "Vault ping"])
        if threat != "None":
            self.status_label.config(text=f"⚠️ Threat Detected: {threat}")
        else:
            self.status_label.config(text="🛡️ All Systems Nominal")

if __name__ == "__main__":
    MagicBoxCloakNode()

