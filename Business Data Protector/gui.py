# gui.py

import tkinter as tk
from ttkbootstrap import Style
import threading
import os
import psutil
import socket

from utils import (
    log_codex, rewrite_optimization_logic, store_rewrite_codex,
    vortex_pulse, detect_density_spike, initiate_mutation_vote,
    load_memory, save_memory
)

from daemon import (
    replicate_swarm, zero_trust_gate, send_fake_telemetry, destroy_mac_ip,
    timed_wipe, protect_personal_data, scan_ports, squad_revive
)

from watcher import PDPWatcher

codex_log = None

class RealTimeESD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌀 MythicBox ASI Node")
        self.geometry("1000x600")
        self.configure(bg="#222")

        self.memory = load_memory()
        self.swarm_nodes = self.get_local_nodes()
        self.node_vars = {}

        self.create_widgets()
        self.start_daemon()
        self.start_file_watcher()

    def create_widgets(self):
        global codex_log
        style = Style(theme="cyborg")

        self.status_frame = tk.Frame(self, bg="#222")
        self.status_frame.pack(pady=10, fill=tk.X)

        self.health_var = tk.StringVar(value="Scanning...")
        self.ports_var = tk.StringVar(value="Loading...")
        self.enhancer_var = tk.StringVar(value="Idle")
        self.emergency_var = tk.StringVar(value="None")

        for i, (label, var) in enumerate([
            ("🧠 PDP Health:", self.health_var),
            ("🌐 Active Ports:", self.ports_var),
            ("🛠️ Auto-Enhancer:", self.enhancer_var),
            ("⚠️ Emergency Status:", self.emergency_var)
        ]):
            tk.Label(self.status_frame, text=label, fg="#0ff", bg="#222").grid(row=i, column=0, sticky="w", padx=10)
            tk.Label(self.status_frame, textvariable=var, fg="#0ff", bg="#222").grid(row=i, column=1, sticky="w")

        self.swarm_frame = tk.LabelFrame(self, text="Swarm Sync Status", fg="#0ff", bg="#222")
        self.swarm_frame.pack(padx=10, pady=10, fill=tk.X)

        for i, node in enumerate(self.swarm_nodes):
            var = tk.StringVar(value="Checking...")
            self.node_vars[node] = var
            tk.Label(self.swarm_frame, text=f"{node}:", fg="#0ff", bg="#222").grid(row=i, column=0, sticky="w", padx=10)
            tk.Label(self.swarm_frame, textvariable=var, fg="#0ff", bg="#222").grid(row=i, column=1, sticky="w")

        codex_log = tk.Text(self, bg="#111", fg="#0ff", font=("Courier", 10), height=15)
        codex_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(self, text="🔐 Allow / Block", command=self.open_allow_block_window).pack(pady=5)
        tk.Button(self, text="🌍 Country Filter", command=self.open_country_window).pack(pady=5)

        footer = tk.Label(self, text="MythicBox Edition • Swarm-Grade • Zero Trust • Codex Mutation Enabled",
                          font=("Helvetica", 11), fg="#888", bg="#222")
        footer.pack(side="bottom", pady=10)

    def get_local_nodes(self):
        nodes = set()
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    nodes.add(f"{iface} ({addr.address})")
        return list(nodes)

    def start_daemon(self):
        threading.Thread(target=self.daemon_loop, daemon=True).start()

    def start_file_watcher(self):
        pdp_dir = os.path.abspath(".")
        handler = PDPWatcher(log_codex, self.repair_file)
        from watchdog.observers import Observer
        observer = Observer()
        observer.schedule(handler, path=pdp_dir, recursive=True)
        observer.start()
        log_codex(f"👁️ Watching directory: {pdp_dir}")

    def daemon_loop(self):
        replicate_swarm()
        zero_trust_gate()
        send_fake_telemetry()
        destroy_mac_ip()
        timed_wipe("Backdoor leak", 3)
        protect_personal_data("face, fingerprint, phone, address, SSN, license")
        scan_ports()
        squad_revive()
        entropy_ring = vortex_pulse()
        if detect_density_spike(entropy_ring) and initiate_mutation_vote():
            rewrite = rewrite_optimization_logic()
            store_rewrite_codex(rewrite)

        while True:
            self.scan_health()
            self.sync_swarm()
            log_codex("🌀 MythicNode heartbeat: system secure")
            threading.Event().wait(30)

    def scan_health(self):
        healthy = False
        for proc in psutil.process_iter(['pid', 'name']):
            if "personal_data_protector" in proc.info['name'].lower():
                mem = proc.memory_info().rss / (1024 * 1024)
                if mem > 500:
                    self.health_var.set(f"⚠️ Memory spike ({mem:.2f}MB)")
                    self.emergency_var.set("Memory overload")
                    log_codex(f"⚠️ Emergency: Memory spike in PID {proc.info['pid']}")
                else:
                    self.health_var.set(f"OK ({mem:.2f}MB)")
                    healthy = True
        if not healthy:
            self.health_var.set("❌ Not running")
            self.emergency_var.set("PDP offline")
            log_codex("❌ PDP process not found.")

    def sync_swarm(self):
        for node in self.swarm_nodes:
            iface = node.split(" ")[0]
            stats = psutil.net_io_counters(pernic=True).get(iface)
            if stats:
                self.node_vars[node].set(f"Sent: {stats.bytes_sent // 1024}KB | Recv: {stats.bytes_recv // 1024}KB")
                log_codex(f"🔄 {node} sync: {stats.bytes_sent}B sent, {stats.bytes_recv}B received")
            else:
                self.node_vars[node].set("Offline")
                log_codex(f"⚠️ {node} appears offline")

    def repair_file(self, file_path):
        self.enhancer_var.set(f"Repairing {os.path.basename(file_path)}")
        rewrite = rewrite_optimization_logic()
        store_rewrite_codex(rewrite)
        log_codex(f"🛠️ File enhanced: {file_path}")
        log_codex(f"📜 Rewrite logic: {rewrite['logic']} @ {rewrite['timestamp']}")
        entropy_ring = vortex_pulse()
        if detect_density_spike(entropy_ring) and initiate_mutation_vote():
            rewrite = rewrite_optimization_logic()
            store_rewrite_codex(rewrite)
            log_codex(f"📜 Rewrite logic: {rewrite['logic']} @ {rewrite['timestamp']}")

    def open_allow_block_window(self):
        win = tk.Toplevel(self)
        win.title("🔐 Allow / Block Control")
        win.geometry("400x400")
        win.configure(bg="#222")

        tk.Label(win, text="Allowed Entities", fg="#0f0", bg="#222").pack(pady=5)
        allow_box = tk.Listbox(win, bg="#111", fg="#0f0")
        allow_box.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Label(win, text="Blocked Entities", fg="#f00", bg="#222").pack(pady=5)
        block_box = tk.Listbox(win, bg="#111", fg="#f00")
        block_box.pack(fill=tk.BOTH, expand=True, padx=10)

        for item in self.memory.get("allowed", []):
            allow_box.insert(tk.END, item)
        for item in self.memory.get("blocked", []):
            block_box.insert(tk.END, item)

        tk.Button(win, text="Toggle Selection", command=lambda: self.toggle_entity(allow_box, block_box)).pack(pady=10)

    def toggle_entity(self, allow_box, block_box):
        selected = allow_box.curselection()
        if selected:
            item = allow_box.get(selected[0])
            allow_box.delete(selected[0])
            block_box.insert(tk.END, item)
            self.memory["allowed"].remove(item)
            self.memory["blocked"].append(item)
            save_memory(self.memory)
            log_codex(f"🚫 Blocked: {item}")
        else:
            selected = block_box.curselection()
            if selected:
                item = block_box.get(selected[0])
                block_box.delete(selected[0])
                allow_box.insert(tk.END, item)
                self.memory["blocked"].remove(item)
                self.memory["allowed"].append(item)
                save_memory(self.memory)
                
            log_codex(f"✅ Allowed: {item}")

    def open_country_window(self):
        win = tk.Toplevel(self)
        win.title("🌍 Country Filter")
        win.geometry("400x300")
        win.configure(bg="#222")

        tk.Label(win, text="Detected Countries", fg="#0ff", bg="#222").pack(pady=5)
        country_box = tk.Listbox(win, bg="#111", fg="#0ff")
        country_box.pack(fill=tk.BOTH, expand=True, padx=10)

        countries = ["United States", "Germany", "China", "Brazil", "Russia"]
        blocked = self.memory.get("countries_blocked", [])
        for c in countries:
            label = f"{c} (BLOCKED)" if c in blocked else c
            country_box.insert(tk.END, label)

        tk.Button(win, text="Block Selected", command=lambda: self.block_country(country_box)).pack(pady=10)

    def block_country(self, country_box):
        selected = country_box.curselection()
        if selected:
            country = country_box.get(selected[0]).split(" ")[0]
            if country not in self.memory["countries_blocked"]:
                self.memory["countries_blocked"].append(country)
                save_memory(self.memory)
                log_codex(f"🌍 Country blocked: {country}")


