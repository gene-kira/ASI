# === magicbox_main.py ===
import tkinter as tk
from tkinter import Canvas
import threading, uuid, psutil, socket, time
import magicbox_core as core  # ✅ Corrected import

# === GUI ===
class MythicFace:
    def __init__(self, brain):
        self.brain = brain
        theme = core.CONFIG["colors"][core.CONFIG["theme"]]
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox ASI Sentinel")
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
        theme = core.CONFIG["colors"][core.CONFIG["theme"]]
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

# === BRAIN ===
class MagicBoxBrain:
    def __init__(self):
        self.vault = core.VaultCore()
        self.memory = core.MemoryCore()
        self.gui = MythicFace(self)
        self.evolver = core.SelfEvolver(self)

    def start(self):
        self.gui.update_status("Initializing...")
        threading.Thread(target=self.monitor_network, daemon=True).start()
        threading.Thread(target=self.scan_processes, daemon=True).start()
        threading.Thread(target=self.mutate_identity, daemon=True, name="Mutator").start()
        threading.Thread(target=self.rebirth_cycle, daemon=True).start()
        threading.Thread(target=self.evolver.monitor_health, daemon=True).start()
        self.gui.update_status("Monitoring threats...")

    def monitor_network(self):
        while True:
            conns = psutil.net_connections(kind='inet')
            for conn in conns:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip, port = conn.raddr
                    if port in core.CONFIG["suspicious_ports"]:
                        self.gui.update_status(f"⚠️ Suspicious connection: {ip}:{port}")
            time.sleep(5)

    def scan_processes(self):
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                name = proc.info['name']
                if name and name.lower() in core.CONFIG["rogue_processes"]:
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
            time.sleep(core.CONFIG["rebirth_interval"])

# === RUN ===
if __name__ == "__main__":
    brain = MagicBoxBrain()
    brain.gui.run()

