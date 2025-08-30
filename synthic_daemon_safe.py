# synthic_daemon_safe.py

import asyncio
import numpy as np
import json
import os
import sys
import subprocess
import platform
import random
from datetime import datetime
from uuid import uuid4
import tkinter as tk
from tkinter import ttk
import threading

# 🔐 Autoloader
def elevate_permissions():
    print(f"🔐 Elevation check: {platform.system()}")

def load_dependencies():
    required = ["numpy"]
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ Package ready → {pkg}")
        except ImportError:
            print(f"📦 Installing → {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# 📜 CodexVault
class CodexVault:
    def __init__(self, vault_path="vault_log.json"):
        self.vault_path = vault_path
        if not os.path.exists(self.vault_path):
            with open(self.vault_path, "w") as f:
                json.dump([], f)

    def log(self, entry):
        entry["logged_at"] = datetime.utcnow().isoformat()
        vault = self._load()
        vault.append(entry)
        self._save(vault)
        print(f"📜 Mutation logged → {entry['id']}")

    def _load(self):
        with open(self.vault_path, "r") as f:
            return json.load(f)

    def _save(self, vault):
        with open(self.vault_path, "w") as f:
            json.dump(vault, f, indent=2)

# 🗳️ SwarmSync
class SwarmSync:
    def __init__(self):
        self.peers = [f"node-{i}" for i in range(1, 6)]

    async def emit_vote(self, payload):
        print(f"🗳️ Emitting vote → {payload['mutation']}")
        await asyncio.sleep(0.1)

# 🌌 MythicOverlay
class MythicOverlay:
    def __init__(self, gui=None):
        self.gui = gui

    def emit_density(self, density):
        symbol = self._symbol(density)
        print(f"🌌 Density → {density:.4f} [{symbol}]")
        if self.gui:
            self.gui.update_density(density)

    def replay_mutation(self, mutation_id, density):
        print(f"🎞️ Replaying mutation → {mutation_id}")
        if self.gui:
            self.gui.add_mutation(mutation_id, density)

    def _symbol(self, d):
        return "🔥" if d > 0.9 else "⚡" if d > 0.6 else "🌿" if d > 0.3 else "💤"

# 🖥️ GUI Dashboard
class MythicDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Synthic Daemon")
        self.geometry("800x500")
        self.configure(bg="#0f0f1f")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Symbolic Density", font=("Helvetica", 14),
                 fg="#ffffff", bg="#0f0f1f").pack()
        self.density_var = tk.DoubleVar()
        ttk.Progressbar(self, orient="horizontal", length=400,
                        mode="determinate", variable=self.density_var).pack(pady=5)

        tk.Label(self, text="Mutation Trail", font=("Helvetica", 14),
                 fg="#ffffff", bg="#0f0f1f").pack()
        self.mutation_list = tk.Listbox(self, width=80, height=6, bg="#1f1f2f",
                                        fg="#00ffcc", font=("Courier", 10))
        self.mutation_list.pack()

        tk.Label(self, text="Swarm Pulse", font=("Helvetica", 14),
                 fg="#ffffff", bg="#0f0f1f").pack()
        self.swarm_label = tk.Label(self, text="Awaiting sync...", font=("Courier", 12),
                                    fg="#ff66cc", bg="#0f0f1f")
        self.swarm_label.pack()

    def update_density(self, density):
        self.density_var.set(density * 100)

    def add_mutation(self, mutation_id, density):
        self.mutation_list.insert(tk.END, f"{mutation_id} | Density: {density:.4f}")

    def update_swarm(self, peers):
        self.swarm_label.config(text=f"Synced with: {', '.join(peers)}")

# 🧬 PulseDaemon (Safe Mode)
class PulseDaemon:
    def __init__(self, gui=None):
        self.codex = CodexVault()
        self.swarm = SwarmSync()
        self.overlay = MythicOverlay(gui=gui)
        self.node_id = f"node-{uuid4()}"
        self.last_mutation = None
        self.gui = gui

    def compute_entropy(self, data):
        probs, _ = np.histogram(data, bins=256)
        probs = probs / np.sum(probs)
        entropy = -np.sum(probs * np.log2(probs + 1e-9))
        return entropy

    def update_density(self, entropy):
        density = np.tanh(entropy / 8.0)
        self.overlay.emit_density(density)
        return density

    def log_mutation(self, entropy, density):
        mutation_id = f"mut-{uuid4()}"
        self.codex.log({
            "id": mutation_id,
            "entropy": entropy,
            "density": density,
            "node": self.node_id
        })
        self.last_mutation = mutation_id
        self.overlay.replay_mutation(mutation_id, density)

    async def transmit(self, density):
        payload = {
            "node": self.node_id,
            "mutation": self.last_mutation,
            "density": density
        }
        await self.swarm.emit_vote(payload)
        if self.gui:
            self.gui.update_swarm(self.swarm.peers)

    async def run(self):
        while True:
            data = np.random.rand(1024)
            entropy = self.compute_entropy(data)
            density = self.update_density(entropy)
            self.log_mutation(entropy, density)
            await self.transmit(density)
            await asyncio.sleep(1.5)

# 🚀 Launch
def launch():
    elevate_permissions()
    load_dependencies()

    gui = MythicDashboard()

    async def start_daemon():
        daemon = PulseDaemon(gui=gui)
        await daemon.run()

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_daemon())

    threading.Thread(target=run_async, daemon=True).start()
    gui.mainloop()

if __name__ == "__main__":
    launch()

