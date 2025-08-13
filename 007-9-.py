import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import psutil
import random
import ctypes
import sys
import os

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
    def rebirth(self):
        return "🔁 Vault reborn with fresh encryption."

class Telemetry:
    def generate_fake(self):
        return f"📡 Fake telemetry: {random.randint(1000,9999)} packets sent."

class MACMutator:
    def randomize(self):
        return f"🌀 MAC randomized to: 02:00:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"

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
class MythicGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ MagicBox Cloak Node")
        self.root.geometry("700x700")
        self.root.configure(bg="#1e1e2f")

        self.vault = Vault()
        self.telemetry = Telemetry()
        self.mac = MACMutator()
        self.responder = AutoResponder()
        self.analyzer = ThreatAnalyzer()
        self.scanner = IPScanner()

        self.whitelist = set()
        self.blocklist = set()
        self.detected_ips = {}

        self.scan_interval = 60
        self.scanning_active = True

        self.build_gui()
        self.auto_scan_on_start()
        threading.Thread(target=self.periodic_scan, daemon=True).start()

    def build_gui(self):
        ttk.Label(self.root, text="🧙‍♂️ Mythic Defense Console", font=("Consolas", 16)).pack(pady=10)

        ttk.Button(self.root, text="🔃 Manual Rescan", command=self.scan_and_defend).pack(pady=5)
        ttk.Button(self.root, text="🌀 MAC Randomize", command=self.randomize_mac).pack(pady=5)
        ttk.Button(self.root, text="🔁 Vault Rebirth", command=self.rebirth_vault).pack(pady=5)
        ttk.Button(self.root, text="📡 Generate Fake Telemetry", command=self.fake_telemetry).pack(pady=5)

        ttk.Label(self.root, text="📋 IP Status List").pack(pady=5)
        self.ip_list = tk.Listbox(self.root, height=10)
        self.ip_list.pack(pady=5)

        ttk.Button(self.root, text="✅ Allow Selected IP", command=self.allow_selected_ip).pack(pady=2)
        ttk.Button(self.root, text="⛔ Block Selected IP", command=self.block_selected_ip).pack(pady=2)

        ttk.Label(self.root, text="✍️ Manual IP Entry").pack(pady=5)
        self.manual_ip_entry = ttk.Entry(self.root)
        self.manual_ip_entry.pack(pady=5)
        ttk.Button(self.root, text="✅ Allow Manual IP", command=self.allow_manual_ip).pack(pady=2)
        ttk.Button(self.root, text="⛔ Block Manual IP", command=self.block_manual_ip).pack(pady=2)

        ttk.Label(self.root, text="⏱️ Set Scan Interval (sec)").pack(pady=5)
        self.interval_entry = ttk.Entry(self.root)
        self.interval_entry.pack(pady=5)
        ttk.Button(self.root, text="✅ Update Interval", command=self.update_interval).pack(pady=5)

        self.output = tk.Text(self.root, height=15, bg="#2e2e3f", fg="#ffffff")
        self.output.pack(pady=10)

    def auto_scan_on_start(self):
        self.output.insert(tk.END, "🚀 Auto-scan initiated...\n")
        threading.Thread(target=self.scan_and_defend, daemon=True).start()

    def periodic_scan(self):
        while self.scanning_active:
            self.scan_and_defend()
            threading.Event().wait(self.scan_interval)

    def update_interval(self):
        try:
            val = int(self.interval_entry.get())
            if val > 0:
                self.scan_interval = val
                self.output.insert(tk.END, f"⏱️ Scan interval updated to {val} seconds.\n")
            else:
                raise ValueError
        except ValueError:
            self.output.insert(tk.END, "⚠️ Invalid interval. Enter a positive integer.\n")

    def scan_and_defend(self):
        ips = self.scanner.scan()
        for ip in ips:
            if ip not in self.detected_ips:
                score = self.analyzer.score(ip)
                self.detected_ips[ip] = score
                self.output.insert(tk.END, f"🧠 {ip} → Threat Score: {score}\n")
                if score > 70 and ip not in self.whitelist and ip not in self.blocklist:
                    success = self.responder.block_ip(ip)
                    if success:
                        self.blocklist.add(ip)
                        self.output.insert(tk.END, f"⛔ Auto-blocked {ip}\n")
                    else:
                        self.output.insert(tk.END, f"⚠️ Failed to block {ip}\n")
        self.refresh_ip_list()

    def refresh_ip_list(self):
        self.ip_list.delete(0, tk.END)
        for ip, score in self.detected_ips.items():
            status = "✅ Allowed" if ip in self.whitelist else "⛔ Blocked" if ip in self.blocklist else "⚠️ Unknown"
            self.ip_list.insert(tk.END, f"{ip} → {status} (Score: {score})")

    def allow_selected_ip(self):
        try:
            selected = self.ip_list.get(tk.ACTIVE)
            ip = selected.split("→")[0].strip()
            self.whitelist.add(ip)
            self.blocklist.discard(ip)
            self.output.insert(tk.END, f"✅ Allowed {ip}\n")
            self.refresh_ip_list()
        except:
            self.output.insert(tk.END, "⚠️ No IP selected.\n")

    def block_selected_ip(self):
        try:
            selected = self.ip_list.get(tk.ACTIVE)
            ip = selected.split("→")[0].strip()
            success = self.responder.block_ip(ip)
            if success:
                self.blocklist.add(ip)
                self.whitelist.discard(ip)
                self.output.insert(tk.END, f"⛔ Blocked {ip}\n")
                self.refresh_ip_list()
            else:
                self.output.insert(tk.END, f"⚠️ Failed to block {ip}\n")
        except:
            self.output.insert(tk.END, "⚠️ No IP selected.\n")

    def allow_manual_ip(self):
        ip = self.manual_ip_entry.get().strip()
        if ip:
            self.whitelist.add(ip)
            self.blocklist.discard(ip)
            self.detected_ips[ip] = self.analyzer.score(ip)
            self.output.insert(tk.END, f"✅ Manually allowed {ip}\n")
            self.refresh_ip_list()

    def block_manual_ip(self):
        ip = self.manual_ip_entry.get().strip()
        if ip:
            success = self.responder.block_ip(ip)
            if success:
                self.blocklist.add(ip)
                self.whitelist.discard(ip)
                self.detected_ips[ip] = self.analyzer.score(ip)
                self.output.insert(tk.END, f"⛔ Manually blocked {ip}\n")
                self.refresh_ip_list()
            else:
                self.output.insert(tk.END, f"⚠️ Failed to block {ip}\n")

    def randomize_mac(self):
        msg = self.mac.randomize()
        self.output.insert(tk.END, msg + "\n")

    def rebirth_vault(self):
        msg = self.vault.rebirth()
        self.output.insert(tk.END, msg + "\n")

    def fake_telemetry(self):
        msg = self.telemetry.generate

    def fake_telemetry(self):
        msg = self.telemetry.generate_fake()
        self.output.insert(tk.END, msg + "\n")

# 🚀 Launch the Mythic Node
ensure_admin()
MythicGUI().root.mainloop()

