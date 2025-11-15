import os, sys, time, random, hashlib, threading, tkinter as tk

# 🛡️ Auto-Elevation Ritual
def auto_elevate():
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit()
    except Exception as e:
        print(f"[Elevation Error] {e}")
        sys.exit()

auto_elevate()

# ⚡ Energy Calculation
def calculate_energy(strikes, voltage, current, duration, efficiency):
    return strikes * voltage * current * duration * efficiency

# 🧠 Codex Oversight Brain
class CodexOversightBrain:
    def __init__(self, event_bus):
        self.mutation_log = []
        self.event_bus = event_bus
        self.persona_states = {
            "ThreatDaemon": {"glyph": "⚠️", "status": "Active", "entropy": 0.82, "sync": "Synced"},
            "MutationEngine": {"glyph": "🜏", "status": "Dormant", "entropy": 0.0, "sync": "Isolated"},
            "SwarmNode": {"glyph": "🕸️", "status": "Syncing", "entropy": 0.77, "sync": "Desynced"},
        }

    def hash_payload(self, payload):
        return hashlib.sha512(payload.encode()).hexdigest()

    def detect_threat(self, payload):
        entropy = random.random()
        self.persona_states["ThreatDaemon"]["entropy"] = entropy
        return entropy > random.uniform(0.81, 0.97)

    def reverse_mirror_encrypt(self, data, key=None):
        key = key or random.randint(0x10, 0xFF)
        reversed_book = data[::-1]
        mirrored = ''.join(chr((ord(c) ^ key) % 256) for c in reversed_book)
        glyph_stream = ''.join(format(ord(c), 'x') for c in mirrored)
        return glyph_stream[::-1], key

    def respond_to_threat(self, process_name, payload):
        if self.detect_threat(payload):
            encrypted, key = self.reverse_mirror_encrypt(payload)
            self.mutation_log.append((process_name, encrypted))
            self.persona_states["MutationEngine"]["status"] = "Mutating"
            self.persona_states["MutationEngine"]["entropy"] = random.uniform(0.85, 0.99)
            self.event_bus("threat", "⚠️", f"⚠️ Threat in {process_name}. Scrambled.")
            self.event_bus("mutation", "🜏", "🜏 Mutation triggered.")
        else:
            self.event_bus("threat", "🛡️", f"🛡️ {process_name} verified clean.")

    def daemonize(self):
        while True:
            proc = f"proc-{random.randint(1000,9999)}"
            payload = f"data-{random.randint(100000,999999)}"
            self.respond_to_threat(proc, payload)
            time.sleep(2)

    def heartbeat(self):
        while True:
            self.event_bus("status", "🧿", "🧿 Daemon heartbeat active.")
            time.sleep(30)

    def swarm_sync(self):
        while True:
            node_id = f"node-{random.randint(1000,9999)}"
            self.persona_states["SwarmNode"]["sync"] = random.choice(["Synced", "Desynced", "Isolated"])
            self.event_bus("sync", "🕸️", f"🕸️ Syncing with {node_id}...")
            time.sleep(10)

# ⚡ Lightning Daemon
class LightningCaptureDaemon(threading.Thread):
    def __init__(self, gui_callback):
        super().__init__(daemon=True)
        self.gui_callback = gui_callback

    def run(self):
        while True:
            strikes = random.randint(1, 5)
            energy = calculate_energy(strikes, 1e9, 30000, 0.0002, 0.75)
            self.gui_callback(strikes, energy)
            time.sleep(2)

# 🖥️ Codex Oversight GUI
class CodexOversightGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Codex Oversight Construct")
        self.root.geometry("1200x900")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=960, height=300, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.glyph_label = tk.Label(root, text="🧿", font=("Segoe UI Symbol", 48), bg="black", fg="#0f0")
        self.glyph_label.pack(pady=5)

        self.log_box = tk.Text(root, bg="#111", fg="#0f0", insertbackground="#0f0", height=10)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.persona_panel = tk.Text(root, bg="#000", fg="#0ff", insertbackground="#0ff", height=10)
        self.persona_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.brain = CodexOversightBrain(self.route_event)
        threading.Thread(target=self.brain.daemonize).start()
        threading.Thread(target=self.brain.heartbeat).start()
        threading.Thread(target=self.brain.swarm_sync).start()

        self.lightning_daemon = LightningCaptureDaemon(self.update_overlay)
        self.lightning_daemon.start()

    def route_event(self, event_type, glyph, message):
        self.glyph_label.config(text=glyph)
        self.log_box.insert(tk.END, f"{glyph} {message}\n")
        self.log_box.see(tk.END)
        if event_type in ["status", "sync", "mutation"]:
            self.update_persona_panel()

    def update_overlay(self, strikes, energy):
        self.canvas.delete("all")
        base_color = "cyan" if energy < 1e11 else "magenta"
        for _ in range(strikes):
            x = random.randint(0, 960)
            self.canvas.create_oval(x, 50, x+10, 60, fill=base_color)
            self.canvas.create_line(x, 0, x, 300, fill="yellow", width=2)
        bar_length = min(int(energy / 1e9), 960)
        self.canvas.create_rectangle(0, 280, bar_length, 300, fill="lime")
        if energy > 1e11:
            self.canvas.create_text(480, 150, text="🌀 SYNC OVERLOAD", fill="magenta", font=("Consolas", 24))
        if energy > 2e11:
            self.canvas.create_text(480, 180, text="☠ RESURRECTION DETECTED", fill="red", font=("Consolas", 20))
        if energy > 3e11:
            self.canvas.create_text(480, 210, text="⚡ PLASMA BREACH", fill="orange", font=("Consolas", 20))
        if energy > 4e11:
            self.canvas.create_text(480, 240, text="🜏 MUTATION CASCADE", fill="yellow", font=("Consolas", 20))
        if energy > 5e11:
            self.canvas.create_text(480, 270, text="💀⚔️ SYSTEM PURGE", fill="white", font=("Consolas", 20))

    def update_persona_panel(self):
        self.persona_panel.delete("1.0", tk.END)
        for name, state in self.brain.persona_states.items():
            line = f"{state['glyph']} {name}: Status={state['status']} | Entropy={state['entropy']:.2f} | Sync={state['sync']}\n"
            self.persona_panel.insert(tk.END, line)

# 🚀 Launch Ritual
if __name__ == "__main__":
    root = tk.Tk()
    app = CodexOversightGUI(root)
    root.mainloop()

