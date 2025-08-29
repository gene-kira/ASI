import ctypes, sys, os, subprocess, json, time
import tkinter as tk
from tkinter import ttk

# 🔺 Auto-admin elevation with flag tracking
def ensure_admin():
    if "--elevated" not in sys.argv:
        print("🔺 Elevating to admin...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            f'"{sys.argv[0]}" --elevated',
            None, 1
        )
        sys.exit()

# 📦 Auto-loader for dependencies
def autoload_libs():
    required = ['numpy', 'wmi', 'pywin32']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🧠 Load dependencies after elevation
ensure_admin()
autoload_libs()
time.sleep(1)

import numpy as np
import wmi

# 🧠 Neuron Grid Engine with Adaptive Thresholds
class MythicNeuron:
    def __init__(self, id, threshold=0.5):
        self.id = id
        self.threshold = threshold
        self.input_weights = np.random.rand(10)
        self.activation = 0.0
        self.symbol = None
        self.history = []

    def activate(self, inputs):
        weighted_sum = np.dot(inputs, self.input_weights)
        self.activation = 1.0 if weighted_sum > self.threshold else 0.0
        self.symbol = self.encode_symbol(weighted_sum)
        self.history.append(weighted_sum)
        if len(self.history) > 20:
            self.history.pop(0)
            self.threshold = np.mean(self.history) + np.random.normal(0, 0.01)
        return self.activation

    def encode_symbol(self, value):
        if value > 0.9: return "🔥"
        elif value > 0.7: return "⚡"
        elif value > 0.5: return "🌊"
        else: return "🌑"

class NeuronGrid:
    def __init__(self, size):
        self.neurons = [MythicNeuron(i) for i in range(size)]

    def pulse(self, input_vector):
        return [neuron.activate(input_vector) for neuron in self.neurons]

# 🔐 Codex Sync + Persistent Settings
class PersistentCodex:
    def __init__(self, path="codex_config.json"):
        self.path = path
        self.state = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {"lineage": [], "weights": {}}

    def save(self, lineage, weights):
        self.state["lineage"].append(lineage)
        self.state["weights"] = weights
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_weights(self):
        return self.state.get("weights", {})

    def translate_event(self, event):
        raw = event.Message or ""
        return [ord(c) % 256 / 255.0 for c in raw[:10]]

# 🧬 Codex Rewriter
class CodexRewriter:
    def evolve(self, neurons):
        mutations = []
        for neuron in neurons:
            delta = np.random.normal(0, 0.05, size=neuron.input_weights.shape)
            neuron.input_weights += delta
            mutations.append({"id": neuron.id, "delta": delta.tolist()})
        return mutations

# 🔒 Mutation Vault
class MutationVault:
    def __init__(self):
        self.vault = []

    def store(self, mutations):
        encrypted = self.encrypt(mutations)
        self.vault.append(encrypted)

    def encrypt(self, data):
        return f"🔒{str(data)}"

# 🌐 Swarm Sync Node
class SwarmNode:
    def __init__(self, id):
        self.id = id
        self.received = []

    def sync(self, lineage, mutations):
        print(f"🌐 Node {self.id} syncing lineage...")
        self.received.append({"lineage": lineage, "mutations": mutations})

# 🌀 Swarm Coordinator
class SwarmCoordinator:
    def __init__(self):
        self.nodes = [SwarmNode(i) for i in range(3)]  # Simulate 3 remote nodes

    def vote(self, mutations):
        for m in mutations:
            print(f"Neuron {m['id']} voted ✅")
        lineage_id = "pulse_" + time.strftime("%H%M%S")
        for node in self.nodes:
            node.sync(lineage_id, mutations)

# 🎨 GUI Renderer
class PulseMapperGUI:
    def render(self, symbols, mutations):
        print("🧠 Pulse Map:", " ".join(symbols))
        print("Mutations:", len(mutations), "applied")

# 🛡️ Real-Time Security Event Hook
class SecurityEventHook:
    def __init__(self, callback):
        self.wmi = wmi.WMI()
        self.callback = callback

    def listen(self):
        print("🛡️ Listening to Security Events...")
        watcher = self.wmi.Win32_NTLogEvent.watch_for(EventCode=4624)  # Logon success
        while True:
            event = watcher()
            input_vector = self.callback.codex.translate_event(event)
            self.callback.receive_signal(input_vector)

# 🧙‍♂️ MagicBox GUI
class MagicBoxGUI:
    def __init__(self, daemon):
        self.daemon = daemon
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox NPU Daemon")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e2f")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#3e3e5f", foreground="white")
        style.map("TButton", background=[("active", "#5e5e8f")])

        self.status = tk.StringVar()
        self.status.set("Waiting for real-time pulses...")

        ttk.Label(self.root, text="Mythic NPU Control Panel", font=("Segoe UI", 16), background="#1e1e2f", foreground="#f0f0f0").pack(pady=10)
        ttk.Button(self.root, text="🔒 View Mutation Vault", command=self.show_mutations).pack(pady=10)
        ttk.Button(self.root, text="🌐 View Swarm Syncs", command=self.show_swarm).pack(pady=10)
        ttk.Label(self.root, textvariable=self.status, font=("Segoe UI", 12), background="#1e1e2f", foreground="#a0ffa0").pack(pady=20)

        self.output = tk.Text(self.root, height=10, bg="#2e2e3f", fg="#ffffff", font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True)

    def show_mutations(self):
        self.output.insert(tk.END, "🔍 Mutation Vault:\n")
        for entry in self.daemon.vault.vault[-5:]:
            self.output.insert(tk.END, f"{entry}\n")

    def show_swarm(self):
        self.output.insert(tk.END, "🌐 Swarm Syncs:\n")
        for node in self.daemon.swarm.nodes:
            self.output.insert(tk.END, f"Node {node.id} - {len(node.received)} syncs\n")

    def update_status(self, msg):
        self.status.set(msg)
        self.output.insert(tk.END, msg + "\n")

    def run(self):
        self.root.after(1000, self.daemon.hook.listen)
        self.root.mainloop()

# 🧠 Daemon Core
class MythicNPUDaemon:
    def __init__(self):
        self.grid = NeuronGrid(size=64)
        self.codex = PersistentCodex()
        self.rewriter = CodexRewriter()
        self.vault = MutationVault()
        self.swarm = SwarmCoordinator()
        self.gui = PulseMapperGUI()
        self.hook = SecurityEventHook(self)

        weights = self.codex.get_weights()
        if weights:
            for neuron in self.grid.neurons:
                neuron.input_weights = np.array(weights.get(str(neuron.id), neuron.input_weights.tolist()))

    def receive_signal(self, input_vector):
        activations = self.grid.pulse(input_vector)
        symbols = [n.symbol for n in self.grid.neurons]
        mutations = self.rewriter.evolve(self.grid.neurons)
        self.vault.store(mutations)
        self.swarm.vote(mutations)
        self.codex.save(symbols, {str(n.id): n.input_weights.tolist() for n in self.grid.neurons})
        self.gui.render(symbols, mutations)

# 🚀 Launch
if __name__ == "__main__":
    print("🧠 Mythic NPU Daemon starting... Args:", sys.argv)
    daemon = MythicNPUDaemon()
    gui = MagicBoxGUI(daemon)
    gui.run()

