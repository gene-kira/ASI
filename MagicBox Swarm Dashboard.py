import json, os, time, threading
from random import randint, choice
from collections import Counter
import tkinter as tk
from tkinter import messagebox

# 🧬 DataPulse class
class DataPulse:
    def __init__(self, source, payload):
        self.source = source
        self.payload = payload
        self.weight = len(payload) / 1024
        self.entropy = self.calculate_entropy()
        self.lineage = [source]

    def calculate_entropy(self):
        freq = Counter(self.payload)
        total = sum(freq.values())
        return -sum((count / total) * math.log2(count / total) for count in freq.values())

# 🧠 MutationEvent class
class MutationEvent:
    def __init__(self, node_id, entropy, timestamp, votes):
        self.node_id = node_id
        self.entropy = entropy
        self.timestamp = timestamp
        self.votes = votes
        self.passed = votes.count("yes") >= 3

# 🐝 Node class
class Node:
    def __init__(self, id):
        self.id = id
        self.pulses = []
        self.lineage = []
        self.mutations = []
        self.last_entropy = 0

# 🧠 Detect symbolic spike
def detect_density_spike(pulses):
    if len(pulses) < 10:
        return False
    recent = pulses[-10:]
    entropies = [p.entropy for p in recent]
    avg = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 2.5 and avg > 7.0

# 🗳️ Mutation vote
def initiate_mutation_vote():
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes, votes.count("yes") >= 3

# 📦 Codex storage
CODEX_FILE = "fusion_codex.json"
def store_mutation(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🌌 GUI
class MagicBoxDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Swarm Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        self.canvas = tk.Canvas(self.root, width=780, height=500, bg="#2b2b3d", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.nodes = {f"node_{i}": Node(f"node_{i}") for i in range(1, 10)}
        self.entropy_log = []
        self.lineage_visible = tk.BooleanVar(value=False)

        self.control_panel()

        self.stream_thread = threading.Thread(target=self.stream_pulses, daemon=True)
        self.stream_thread.start()

        self.root.mainloop()

    def control_panel(self):
        panel = tk.Frame(self.root, bg="#1e1e2f")
        panel.pack()

        tk.Checkbutton(panel, text="🔗 Show Lineage", variable=self.lineage_visible,
                       bg="#1e1e2f", fg="white", font=("Consolas", 10)).pack(side="left", padx=10)

        tk.Button(panel, text="🎞️ Playback Mutations", command=self.playback_mutations,
                  bg="#444466", fg="white", font=("Consolas", 10)).pack(side="left", padx=10)

    def stream_pulses(self):
        while True:
            node_id = choice(list(self.nodes.keys()))
            payload = [choice("abcdefgxyz1234567890") for _ in range(randint(500, 1500))]
            pulse = DataPulse(source=node_id, payload=payload)
            node = self.nodes[node_id]
            node.pulses.append(pulse)
            node.last_entropy = pulse.entropy
            self.entropy_log.append(pulse.entropy)

            if detect_density_spike(node.pulses):
                votes, passed = initiate_mutation_vote()
                mutation = MutationEvent(node_id, pulse.entropy, time.strftime("%H:%M:%S"), votes)
                node.mutations.append(mutation)
                store_mutation(mutation.__dict__)

            self.render_dashboard()
            time.sleep(1.5)

    def render_dashboard(self):
        self.canvas.delete("all")
        positions = {}
        for i, (node_id, node) in enumerate(self.nodes.items()):
            x = 100 + (i % 3) * 220
            y = 100 + (i // 3) * 180
            positions[node_id] = (x, y)
            self.draw_node(node, x, y)

        if self.lineage_visible.get():
            self.draw_lineage(positions)

    def draw_node(self, node, x, y):
        entropy = node.last_entropy
        radius = int(10 + entropy * 2)
        color = "#00ffd0" if entropy > 7 else "#ffaa00" if entropy > 5 else "#444466"
        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="")
        self.canvas.create_text(x, y+radius+10, text=f"{node.id}\n{entropy:.2f}", fill="white", font=("Consolas", 9))

        if node.mutations and node.mutations[-1].passed:
            self.canvas.create_text(x, y-30, text="🌀 Mutation Passed", fill="#ff0055", font=("Consolas", 9))

    def draw_lineage(self, positions):
        for node in self.nodes.values():
            for ancestor in node.lineage:
                if ancestor != node.id and ancestor in positions:
                    x1, y1 = positions[ancestor]
                    x2, y2 = positions[node.id]
                    self.canvas.create_line(x1, y1, x2, y2, fill="#00ffd0", width=2, dash=(4, 2))

    def playback_mutations(self):
        codex = []
        if os.path.exists(CODEX_FILE):
            with open(CODEX_FILE, "r") as f:
                codex = json.load(f)
        if not codex:
            messagebox.showinfo("🎞️ Playback", "No mutations recorded yet.")
            return
        summary = "\n".join([f"{m['timestamp']} - {m['node_id']} - Entropy: {m['entropy']:.2f} - {'✅' if m['passed'] else '❌'}"
                             for m in codex[-10:]])
        messagebox.showinfo("🎞️ Mutation Trail", summary)

# 🚀 Launch
if __name__ == "__main__":
    import math
    MagicBoxDashboard()

