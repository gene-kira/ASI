import os, sys, threading, time, uuid, socket, json
try:
    import psutil
except ImportError:
    os.system(f"{sys.executable} -m pip install psutil")
    import psutil

import tkinter as tk
from tkinter import Canvas

# Configurable themes and memory settings
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
    "rebirth_interval": 60
}

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

class MythicFace:
    def __init__(self, brain):
        self.brain = brain
        theme = CONFIG["colors"][CONFIG["theme"]]
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Cloak Node")
        self.root.geometry("900x700")
        self.root.configure(bg=theme["bg"])

        self.canvas = Canvas(self.root, width=900, height=400, bg=theme["bg"], highlightthickness=0)
        self.canvas.pack()

        self.status_label = tk.Label(self.root, text="Status: Idle", fg=theme["text"], bg=theme["bg"], font=("Consolas", 14))
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start MagicBox", command=self.brain.start, font=("Consolas", 14), bg="black", fg=theme["text"])
        self.start_button.pack(pady=10)

        self.log_box = tk.Text(self.root, height=8, bg="black", fg=theme["text"], font=("Consolas", 10))
        self.log_box.pack(fill="x", padx=10)

        self.memory_box = tk.Text(self.root, height=8, bg="#111", fg=theme["text"], font=("Consolas", 10))
        self.memory_box.pack(fill="x", padx=10)
        self.memory_box.insert(tk.END, "🧠 MemoryCore Loaded\n")

        self.particles = []
        self.animate_particles()

    def update_status(self, msg):
        self.status_label.config(text=f"Status: {msg}")
        self.brain.vault.log(msg)
        self.brain.memory.remember(msg)
        self.refresh_logs()
        self.refresh_memory()

    def refresh_logs(self):
        self.log_box.delete(1.0, tk.END)
        for entry in self.brain.vault.logs:
            self.log_box.insert(tk.END, entry + "\n")

    def refresh_memory(self):
        self.memory_box.delete(1.0, tk.END)
        for entry in self.brain.memory.entries[-10:]:
            self.memory_box.insert(tk.END, f"{entry['time']} → {entry['event']}\n")

    def animate_particles(self):
        theme = CONFIG["colors"][CONFIG["theme"]]
        for _ in range(30):
            x, y = uuid.uuid4().int % 900, uuid.uuid4().int % 400
            dot = self.canvas.create_oval(x, y, x+4, y+4, fill=theme["particle"], outline="")
            self.particles.append(dot)
        self.move_particles()

    def move_particles(self):
        for dot in self.particles:
            dx, dy = uuid.uuid4().int % 3 - 1, uuid.uuid4().int % 3 - 1
            self.canvas.move(dot, dx, dy)
        self.root.after(100, self.move_particles)

    def run(self):
        self.root.mainloop()

class MagicBoxBrain:
    def __init__(self):
        self.vault = VaultCore()
        self.memory = MemoryCore()
        self.gui = MythicFace(self)

    def start(self):
        self.gui.update_status("Initializing...")
        threading.Thread(target=self.monitor_network, daemon=True).start()
        threading.Thread(target=self.scan_processes, daemon=True).start()
        threading.Thread(target=self.mutate_identity, daemon=True).start()
        threading.Thread(target=self.rebirth_cycle, daemon=True).start()
        self.gui.update_status("Monitoring threats...")

    def monitor_network(self):
        while True:
            conns = psutil.net_connections(kind='inet')
            for conn in conns:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip, port = conn.raddr
                    if port in CONFIG["suspicious_ports"]:
                        self.gui.update_status(f"⚠️ Suspicious connection: {ip}:{port}")
            time.sleep(5)

    def scan_processes(self):
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                name = proc.info['name']
                if name and name.lower() in CONFIG["rogue_processes"]:
                    self.gui.update_status(f"⚠️ Rogue process detected: {name}")
            time.sleep(10)

    def mutate_identity(self):
        while True:
            mac = ":".join(["%02x" % (uuid.uuid4().int >> i & 0xff) for i in range(0, 48, 8)])
            ip = socket.gethostbyname(socket.gethostname())
            self.gui.update_status(f"🕶️ MAC: {mac} | IP: {ip}")
            time.sleep(10)

    def rebirth_cycle(self):
        while True:
            self.gui.update_status("🔄 Rebirth cycle initiated. Vault purged.")
            self.vault.purge()
            self.gui.refresh_logs()
            time.sleep(CONFIG["rebirth_interval"])

if __name__ == "__main__":
    brain = MagicBoxBrain()
    brain.gui.run()

