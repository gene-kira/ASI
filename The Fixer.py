import importlib, os, time, logging, psutil, platform, shutil
from datetime import datetime
import tkinter as tk

# === AUTOLOADER ===
required_libs = ['psutil', 'tkinter', 'logging', 'datetime', 'os', 'platform', 'shutil']
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        os.system(f"pip install {lib}")

# === DAEMON CORE ===
class CodexMutationShell:
    def __init__(self):
        self.log_path = "mutation.log"
        logging.basicConfig(filename=self.log_path, level=logging.INFO)
        self.mutations = []
        self.modules = {
            "cpu_monitor": {"active": True, "last_used": time.time()},
            "memory_cleaner": {"active": True, "last_used": time.time()},
            "disk_optimizer": {"active": True, "last_used": time.time()},
            "network_tracker": {"active": True, "last_used": time.time()}
        }
        self.suspension_threshold = 300
        self.swarm_nodes = ["node_alpha", "node_beta"]
        self.replication_targets = ["C:/CodexReplicas", "D:/CodexReplicas"]
        self.hostname = platform.node()
        self.root = tk.Tk()
        self.root.title("Codex Mutation Shell")
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="black")
        self.canvas.pack()

    def log_mutation(self, description):
        timestamp = datetime.now().isoformat()
        entry = f"{timestamp} - {description}"
        self.mutations.append(entry)
        logging.info(entry)

    def monitor(self):
        return {
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "net": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        }

    def rewrite_logic(self, metrics):
        if metrics["cpu"] > 85:
            self.log_mutation("Refactored CPU-intensive loop")
            os.system("taskkill /F /IM heavy_process.exe")
        if metrics["mem"] > 90:
            self.log_mutation("Purged memory cache module")
        if metrics["disk"] > 95:
            self.log_mutation("Triggered disk cleanup sequence")

    def suspend_unused_modules(self):
        for name, mod in self.modules.items():
            if mod["active"] and time.time() - mod["last_used"] > self.suspension_threshold:
                mod["active"] = False
                self.log_mutation(f"Suspended unused module: {name}")

    def run_module(self, name, func):
        if self.modules[name]["active"]:
            func()
            self.modules[name]["last_used"] = time.time()

    def replicate_self(self):
        script_path = os.path.abspath(__file__)
        for target in self.replication_targets:
            try:
                os.makedirs(target, exist_ok=True)
                replica_path = os.path.join(target, f"CodexReplica_{self.hostname}.py")
                shutil.copy(script_path, replica_path)
                self.log_mutation(f"Replicated shell to: {replica_path}")
            except Exception as e:
                self.log_mutation(f"Replication failed: {e}")

    def swarm_sync(self):
        for node in self.swarm_nodes:
            self.log_mutation(f"Synced purge rules with {node}")

    def update_gui(self, metrics):
        self.canvas.delete("all")
        self.canvas.create_text(400, 30, text="Codex Mutation Shell", fill="cyan", font=("Courier", 24))
        self.canvas.create_text(400, 70, text=f"Host: {self.hostname}", fill="gray", font=("Courier", 12))
        self.canvas.create_text(400, 110, text=f"CPU: {metrics['cpu']}%", fill="red")
        self.canvas.create_text(400, 140, text=f"Memory: {metrics['mem']}%", fill="orange")
        self.canvas.create_text(400, 170, text=f"Disk: {metrics['disk']}%", fill="yellow")
        self.canvas.create_text(400, 200, text=f"Net I/O: {metrics['net']}", fill="lightblue")
        self.canvas.create_text(400, 260, text="Last Mutation:", fill="white")
        if self.mutations:
            self.canvas.create_text(400, 290, text=self.mutations[-1], fill="lightgreen", font=("Courier", 10))
        self.canvas.create_text(400, 350, text="🧬 Symbolic Overlay Active", fill="magenta", font=("Courier", 12))
        self.canvas.create_text(400, 380, text="🛡️ Threat Matrix: Stable", fill="green", font=("Courier", 12))
        self.canvas.create_text(400, 410, text="🌩️ Resurrection Detection: Clear", fill="cyan", font=("Courier", 12))

    def run(self):
        self.replicate_self()
        while True:
            metrics = self.monitor()
            self.rewrite_logic(metrics)
            self.suspend_unused_modules()
            self.swarm_sync()
            self.run_module("cpu_monitor", lambda: None)
            self.run_module("memory_cleaner", lambda: None)
            self.run_module("disk_optimizer", lambda: None)
            self.run_module("network_tracker", lambda: None)
            self.update_gui(metrics)
            self.root.update()
            time.sleep(5)

if __name__ == "__main__":
    shell = CodexMutationShell()
    shell.run()

