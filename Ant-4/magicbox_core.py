# === magicbox_core.py ===
import os, sys, time, uuid, socket, json, threading
try:
    import psutil
except ImportError:
    os.system(f"{sys.executable} -m pip install psutil")
    import psutil

# === CONFIG ===
CONFIG = {
    "theme": "Dark Oracle",
    "colors": {
        "Dark Oracle": {"bg": "#0f0f1f", "particle": "cyan", "text": "lime"},
        "Neon Swarm": {"bg": "#001f1f", "particle": "magenta", "text": "yellow"}
    },
    "suspicious_ports": [22, 23, 8080, 4444],
    "rogue_processes": ["unknown.exe", "suspicious.exe"],
    "memory_file": "magicbox_memory.json",
    "memory_depth": 100,
    "rebirth_interval": 60,
    "module_path": "magicbox_main.py"
}

# === VAULT ===
class VaultCore:
    def __init__(self):
        self.logs = []
        self.max_logs = 50

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def purge(self):
        self.logs.clear()

# === MEMORY ===
class MemoryCore:
    def __init__(self):
        self.memory_file = CONFIG["memory_file"]
        self.entries = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return []

    def remember(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.entries.append({"time": timestamp, "event": msg})
        if len(self.entries) > CONFIG["memory_depth"]:
            self.entries.pop(0)
        self.save_memory()

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.entries, f, indent=2)

# === SELF-EVOLVER ===
class SelfEvolver:
    def __init__(self, brain):
        self.brain = brain
        self.module_path = CONFIG["module_path"]

    def monitor_health(self):
        while True:
            try:
                if not any(t.name == "Mutator" and t.is_alive() for t in threading.enumerate()):
                    self.brain.gui.update_status("🧠 Mutation thread stalled. Rewriting...")
                    self.rewrite_mutation_logic()
            except Exception as e:
                self.brain.gui.update_status(f"⚠️ Evolver error: {e}")
            time.sleep(15)

    def rewrite_mutation_logic(self):
        try:
            with open(self.module_path, "r") as f:
                code = f.read()
            if "time.sleep(10)" in code:
                mutated = code.replace("time.sleep(10)", "time.sleep(5)")
                with open(self.module_path, "w") as f:
                    f.write(mutated)
                self.brain.memory.remember("🧬 Mutation: sleep(10) → sleep(5)")
                self.brain.gui.update_status("🔄 Mutation applied. Rebirth triggered.")
                self.brain.vault.purge()
                self.brain.gui.refresh_logs()
        except Exception as e:
            self.brain.gui.update_status(f"⚠️ Mutation failed: {e}")

