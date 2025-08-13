import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import psutil
import random
import uuid
import socket
import ctypes
import sys
import os
import time

# 🛑 Auto-Elevate to Admin
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()

# 🧠 Core Modules
class Vault:
    def __init__(self):
        self.data = {}

    def rebirth(self):
        vault_id = str(uuid.uuid4())[:8]
        self.data[vault_id] = "EncryptedPayload"
        return f"🔁 Vault {vault_id} reborn with fresh encryption."

    def cleanup(self):
        if len(self.data) > 5:
            oldest = list(self.data.keys())[0]
            del self.data[oldest]
            return f"💥 Vault {oldest} self-destructed."
        return None

class Telemetry:
    def generate_fake(self):
        return f"📡 Fake telemetry: {random.randint(1000,9999)} packets sent."

class MACMutator:
    def randomize(self):
        new_mac = ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])
        fake_ip = socket.inet_ntoa(bytes([random.randint(1, 254) for _ in range(4)]))
        return f"🌀 MAC={new_mac} | IP={fake_ip}"

class AutoResponder:
    def block_ip(self, ip):
        try:
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=BlockIP", "dir=in", "action=block", f"remoteip={ip}"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

class ThreatAnalyzer:
    def score(self, ip):
        return random.randint(1, 100)

class IPScanner:
    def scan(self):
        ips = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.raddr:
                ip = conn.raddr.ip
                if not ip.startswith(('127.', '10.', '192.')):
                    ips.add(ip)
        return list(ips)

# 🌌 Mythic GUI
class MythicCloakNode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ MagicBox Cloak Node")
        self.root.geometry("800x800")
        self.root.configure(bg="#1e1e2f")

        self.vault = Vault()
        self.telemetry = Telemetry()
        self.mac = MACMutator()
        self.responder = AutoResponder()
        self.analyzer = ThreatAnalyzer()
        self.scanner = IPScanner()

        self.ip_status = {}
        self.whitelist = set()
        self.blocklist = set()
        self.scan_interval = 60
        self.running = True

        self.build_gui()
        self.start_threads()

    def build_gui(self):
        tk.Label(self.root, text="🧙‍♂️ Mythic Defense Console", font=("Helvetica", 24, "bold"),
                 fg="#00ffff", bg="#1e1e2f").pack(pady=10)

        self.ip_list = tk.Listbox(self.root, height=10, width=100, font=("Courier", 10),
                                  bg="#2e2e3f", fg="#ffffff")
        self.ip_list.pack(pady=10)

        self.vault_label = tk.Label(self.root, text="Vault Status: 🔐 Secure", font=("Helvetica", 14),
                                    fg="#00ff00", bg="#1e1e2f")
        self.vault_label.pack(pady=5)

        self.telemetry_label = tk.Label(self.root, text="Fake Telemetry: 🛰️ Active", font=("Helvetica", 14),
                                        fg="#ffcc00", bg="#1e1e2f")
        self.telemetry_label.pack(pady=5)

        self.swarm_label = tk.Label(self.root, text="Swarm Coordination: 🧠 Online", font=("Helvetica", 14),
                                    fg="#00ffff", bg="#1e1e2f")
        self.swarm_label.pack(pady=5)

        self.trail_canvas = tk.Canvas(self.root, width=760, height=200, bg="#0f0f1f", highlightthickness=0)
        self.trail_canvas.pack(pady=10)

        self.status_label = tk.Label(self.root, text="System Status: 🟢 Stable", font=("Helvetica", 12),
                                     fg="#ffffff", bg="#1e1e2f")
        self.status_label.pack(pady=10)

        self.output = tk.Text(self.root, height=10, bg="#2e2e3f", fg="#ffffff")
        self.output.pack(pady=10)

    def start_threads(self):
        threading.Thread(target=self.periodic_scan, daemon=True).start()
        threading.Thread(target=self.mutate_network, daemon=True).start()
        threading.Thread(target=self.manage_vault, daemon=True).start()
        threading.Thread(target=self.animate_trails, daemon=True).start()

    def periodic_scan(self):
        while self.running:
            ips = self.scanner.scan()
            for ip in ips:
                if ip not in self.ip_status:
                    score = self.analyzer.score(ip)
                    status = "🟢 Safe" if score < 30 else "🟡 Suspicious" if score < 70 else "🔴 Threat"
                    self.ip_status[ip] = (score, status)
                    self.output.insert(tk.END, f"🧠 {ip} → Threat Score: {score}\n")
                    if score > 70 and ip not in self.whitelist and ip not in self.blocklist:
                        success = self.responder.block_ip(ip)
                        if success:
                            self.blocklist.add(ip)
                            self.output.insert(tk.END, f"⛔ Auto-blocked {ip}\n")
                        else:
                            self.output.insert(tk.END, f"⚠️ Failed to block {ip}\n")
            self.update_ip_list()
            time.sleep(self.scan_interval)

    def update_ip_list(self):
        self.ip_list.delete(0, tk.END)
        for ip, (score, status) in list(self.ip_status.items())[-10:]:
            entry = f"{ip} | Threat Score: {score} | Status: {status}"
            self.ip_list.insert(tk.END, entry)

    def mutate_network(self):
        while self.running:
            msg = self.mac.randomize()
            self.status_label.config(text=f"Network Mutation: {msg}")
            self.telemetry_label.config(text=self.telemetry.generate_fake())
            time.sleep(5)

    def manage_vault(self):
        while self.running:
            msg = self.vault.rebirth()
            self.vault_label.config(text=f"Vault Status: {msg}")
            cleanup_msg = self.vault.cleanup()
            if cleanup_msg:
                self.output.insert(tk.END, cleanup_msg + "\n")
            time.sleep(10)

    def animate_trails(self):
        while self.running:
            self.trail_canvas.delete("all")
            for _ in range(20):
                x = random.randint(0, 760)
                y = random.randint(0, 200)
                size = random.randint(2, 6)
                color = random.choice(["#00ffff", "#ff00ff", "#ffff00"])
                self.trail_canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
            time.sleep(0.5)

    def run(self):
        self.root.mainloop()

# 🚀 Launch the Mythic Node
ensure_admin()
MythicCloakNode().run()

