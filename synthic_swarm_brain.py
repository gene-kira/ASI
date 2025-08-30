# synthic_swarm_brain.py

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

# 🌌 EmotionalOverlay
class EmotionalOverlay:
    def __init__(self, gui=None):
        self.gui = gui

    def react(self, mutation):
        symbol = self._symbol(mutation["density"])
        print(f"🌌 Emotional Feedback → {mutation['id']} [{symbol}]")
        if self.gui:
            self.gui.update_density(mutation["density"])
            self.gui.add_mutation(mutation["id"], mutation["density"])

    def _symbol(self, d):
        return "🔥" if d > 0.9 else "⚡" if d > 0.6 else "🌿" if d > 0.3 else "💤"

# 🧠 SymbolicMemory
class SymbolicMemory:
    def __init__(self):
        self.trail = []

    def store(self, mutation):
        self.trail.append(mutation)

    def generate_signal(self):
        return np.random.rand(1024)

# 🧬 MutationEngine
class MutationEngine:
    def process(self, signal):
        probs, _ = np.histogram(signal, bins=256)
        probs = probs / np.sum(probs)
        entropy = -np.sum(probs * np.log2(probs + 1e-9))
        density = np.tanh(entropy / 8.0)
        mutation_id = f"mut-{uuid4()}"
        return {
            "id": mutation_id,
            "entropy": entropy,
            "density": density,
            "rewrite": density > 0.85
        }

# 🖥️ GUI Dashboard
class MythicDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Synthic Swarm Brain")
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

# 🧠 SwarmNode
class SwarmNode:
    def __init__(self, node_id, gui=None, parent=None):
        self.node_id = node_id
        self.parent = parent
        self.memory = SymbolicMemory()
        self.engine = MutationEngine()
        self.overlay = EmotionalOverlay(gui=gui)
        self.codex = CodexVault()
        self.swarm = SwarmSync()
        self.children = []
        self.gui = gui

    def replicate(self):
        child_id = f"{self.node_id}-child-{uuid4()}"
        child = SwarmNode(child_id, gui=self.gui, parent=self)
        self.children.append(child)
        print(f"🧬 Node {self.node_id} replicated → {child_id}")
        return child

    def mutate(self):
        signal = self.memory.generate_signal()
        mutation = self.engine.process(signal)
        self.memory.store(mutation)
        self.codex.log({
            "id": mutation["id"],
            "entropy": mutation["entropy"],
            "density": mutation["density"],
            "node": self.node_id
        })
        self.overlay.react(mutation)
        if mutation["rewrite"]:
            self.rewrite_logic(mutation)
        return mutation

    def rewrite_logic(self, mutation):
        print(f"🧠 Node {self.node_id} rewriting logic based on mutation: {mutation['id']}")
        if mutation["density"] > 0.95:
            self.replicate()

    async def pulse(self):
        while True:
            mutation = self.mutate()
            await self.swarm.emit_vote({
                "node": self.node_id,
                "mutation": mutation["id"],
                "density": mutation["density"]
            })
            if self.gui:
                self.gui.update_swarm(self.swarm.peers)
            for child in self.children:
                await child.pulse()
            await asyncio.sleep(1.5)

# 🚀 Launch
def launch():
    elevate_permissions()
    load_dependencies()

    gui = MythicDashboard()

    async def start_swarm():
        root_node = SwarmNode("root-node", gui=gui)
        await root_node.pulse()

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_swarm())

    threading.Thread(target=run_async, daemon=True).start()
    gui.mainloop()

if __name__ == "__main__":
    launch()

