import os, sys, threading, time, uuid, socket, subprocess
try:
    import psutil
except ImportError:
    os.system(f"{sys.executable} -m pip install psutil")
    import psutil

import tkinter as tk
from tkinter import Canvas

class MagicBoxGUI:
    def __init__(self, brain):
        self.brain = brain
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Threat Listener")
        self.root.geometry("700x500")
        self.root.configure(bg="#0f0f1f")

        self.canvas = Canvas(self.root, width=700, height=400, bg="#0f0f1f", highlightthickness=0)
        self.canvas.pack()

        self.status_label = tk.Label(self.root, text="Status: Idle", fg="cyan", bg="#0f0f1f", font=("Consolas", 14))
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start MagicBox", command=self.brain.start, font=("Consolas", 14), bg="black", fg="lime")
        self.start_button.pack(pady=10)

        self.particles = []
        self.animate_particles()

    def update_status(self, msg):
        self.status_label.config(text=f"Status: {msg}")

    def animate_particles(self):
        for _ in range(20):
            x, y = uuid.uuid4().int % 700, uuid.uuid4().int % 400
            dot = self.canvas.create_oval(x, y, x+4, y+4, fill="cyan", outline="")
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
        self.gui = MagicBoxGUI(self)

    def start(self):
        self.gui.update_status("Initializing...")
        threading.Thread(target=self.monitor_network, daemon=True).start()
        threading.Thread(target=self.scan_processes, daemon=True).start()
        threading.Thread(target=self.mutate_identity, daemon=True).start()
        self.gui.update_status("Monitoring threats...")

    def monitor_network(self):
        while True:
            conns = psutil.net_connections(kind='inet')
            for conn in conns:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip, port = conn.raddr
                    if port not in [80, 443, 53]:  # suspicious ports
                        self.gui.update_status(f"Suspicious connection: {ip}:{port}")
            time.sleep(5)

    def scan_processes(self):
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                name = proc.info['name']
                if name and name.lower() in ['unknown.exe', 'suspicious.exe']:
                    self.gui.update_status(f"Rogue process: {name}")
            time.sleep(10)

    def mutate_identity(self):
        while True:
            mac = ":".join(["%02x" % (uuid.uuid4().int >> i & 0xff) for i in range(0, 48, 8)])
            ip = socket.gethostbyname(socket.gethostname())
            self.gui.update_status(f"MAC: {mac} | IP: {ip}")
            time.sleep(10)

if __name__ == "__main__":
    brain = MagicBoxBrain()
    brain.gui.run()

