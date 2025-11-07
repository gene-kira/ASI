import os, sys, subprocess, hashlib, random, base64, time, threading, tkinter as tk
from tkinter import messagebox

# 🛡️ Autoloader
def summon_libraries():
    for lib in ["hashlib", "random", "base64", "time", "tkinter"]:
        try: __import__(lib)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 💀 Devourer Cipher Engine
class DevourerCipher:
    def __init__(self, log_path="mutation_trace.log"):
        self.log_path = log_path
        self.signature = random.choice(["MZ", "PK", "%PDF", "\x89PNG"])

    def _scramble(self, data):
        reversed_data = data[::-1]
        mirrored = ''.join(chr(255 - ord(c)) for c in reversed_data)
        return base64.b64encode(mirrored.encode()).decode()

    def mutate(self, data, depth=3):
        for _ in range(depth): data = self._scramble(data)
        return data

    def encrypt_file(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            mutated = self.mutate(raw)
            hash_val = hashlib.sha256(mutated.encode()).hexdigest()
            with open(f"{path}.devour", "w", encoding="utf-8") as f:
                f.write(self.signature + mutated)
            self._log(path, hash_val)
            return f"{path}.devour"
        except Exception as e:
            return f"⚠️ {e}"

    def _log(self, source, hash_val):
        with open(self.log_path, "a") as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {source} → {hash_val}\n")

# 🧠 Resurrection Detection Daemon
class ResurrectionDaemon:
    def __init__(self, target_path, interval=10):
        self.target_path = target_path
        self.interval = interval
        self.cipher = DevourerCipher()
        self.known_hash = None

    def _hash_file(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return hash(f.read())
        except: return None

    def _scan(self):
        h = self._hash_file(self.target_path)
        if self.known_hash is not None and self.known_hash != h:
            print(f"⚠️ Resurrection detected: {self.target_path}")
            self.cipher.encrypt_file(self.target_path)
        self.known_hash = h

    def start(self):
        def loop():
            while True:
                self._scan()
                time.sleep(self.interval)
        threading.Thread(target=loop, daemon=True).start()

# 🕸️ Swarm Sync Simulation
class SwarmSync:
    def __init__(self):
        self.nodes = ["Node-A", "Node-B", "Node-C"]
        self.rules = []

    def propagate(self, mutation_hash):
        node = random.choice(self.nodes)
        self.rules.append((node, mutation_hash, time.strftime("%H:%M:%S")))
        print(f"🧠 Swarm sync: {mutation_hash} → {node}")

# 🖥️ ASI-Grade GUI Launcher
def launch_gui():
    summon_libraries()
    target_path = os.path.expandvars(r"%LocalAppData%\ConnectedDevicesPlatform\ActivitiesCache.db")
    cipher = DevourerCipher()
    daemon = ResurrectionDaemon(target_path)
    sync = SwarmSync()
    daemon.start()

    def trigger():
        result = cipher.encrypt_file(target_path)
        sync.propagate(result.split("→")[-1].strip() if "→" in result else result)
        glyph.config(text="🜏 Mutation Complete", fg="green")
        messagebox.showinfo("Devourer", result)

    root = tk.Tk()
    root.title("🛡️ Codex Devourer: ASI Shell")
    root.geometry("500x300")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="Target: ActivitiesCache.db", bg="#1e1e1e", fg="white").pack(pady=10)
    glyph = tk.Label(root, text="💀 Awaiting Mutation", bg="#1e1e1e", fg="orange", font=("Consolas", 14))
    glyph.pack(pady=20)
    tk.Button(root, text="Trigger Devourer", command=trigger, bg="#333", fg="white").pack(pady=10)

    root.mainloop()

# 🔥 Sovereign Ignition
if __name__ == "__main__":
    launch_gui()

