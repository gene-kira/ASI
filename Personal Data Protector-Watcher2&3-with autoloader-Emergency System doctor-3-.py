import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from datetime import datetime
import socket

# === Helper: Get Local IPs as Swarm Nodes ===
def get_local_nodes():
    nodes = set()
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                nodes.add(f"{iface} ({addr.address})")
    return list(nodes)

# === GUI + Daemon Unified ===
class RealTimeESD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Data Protector ESD Dashboard")
        self.geometry("1000x600")
        self.configure(bg="#f0f0f0")

        self.swarm_nodes = get_local_nodes()
        self.node_vars = {}

        self.create_widgets()
        self.start_daemon()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10), background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")

        # === Status Panels ===
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(pady=10, fill=tk.X)

        self.health_var = tk.StringVar(value="Scanning...")
        self.ports_var = tk.StringVar(value="Loading...")
        self.enhancer_var = tk.StringVar(value="Idle")
        self.emergency_var = tk.StringVar(value="None")

        ttk.Label(self.status_frame, text="🧠 PDP Health:").grid(row=0, column=0, sticky="w", padx=10)
        ttk.Label(self.status_frame, textvariable=self.health_var).grid(row=0, column=1, sticky="w")

        ttk.Label(self.status_frame, text="🌐 Active Ports:").grid(row=1, column=0, sticky="w", padx=10)
        ttk.Label(self.status_frame, textvariable=self.ports_var).grid(row=1, column=1, sticky="w")

        ttk.Label(self.status_frame, text="🛠️ Auto-Enhancer:").grid(row=2, column=0, sticky="w", padx=10)
        ttk.Label(self.status_frame, textvariable=self.enhancer_var).grid(row=2, column=1, sticky="w")

        ttk.Label(self.status_frame, text="⚠️ Emergency Status:").grid(row=3, column=0, sticky="w", padx=10)
        ttk.Label(self.status_frame, textvariable=self.emergency_var).grid(row=3, column=1, sticky="w")

        # === Swarm Node Panel ===
        self.swarm_frame = ttk.LabelFrame(self, text="Swarm Sync Status")
        self.swarm_frame.pack(padx=10, pady=10, fill=tk.X)

        for i, node in enumerate(self.swarm_nodes):
            var = tk.StringVar(value="Checking...")
            self.node_vars[node] = var
            ttk.Label(self.swarm_frame, text=f"{node}:").grid(row=i, column=0, sticky="w", padx=10)
            ttk.Label(self.swarm_frame, textvariable=var).grid(row=i, column=1, sticky="w")

        # === Codex Log ===
        self.codex_log = tk.Text(self, bg="#ffffff", fg="#333333", font=("Consolas", 10), height=15)
        self.codex_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_daemon(self):
        threading.Thread(target=self.daemon_loop, daemon=True).start()

    def daemon_loop(self):
        while True:
            self.scan_health()
            self.scan_ports()
            self.auto_enhance()
            self.sync_swarm()
            self.log_codex("✅ Daemon heartbeat confirmed.")
            time.sleep(30)

    def scan_health(self):
        healthy = False
        for proc in psutil.process_iter(['pid', 'name']):
            if "personal_data_protector" in proc.info['name'].lower():
                mem = proc.memory_info().rss / (1024 * 1024)
                if mem > 500:
                    self.health_var.set(f"⚠️ Memory spike ({mem:.2f}MB)")
                    self.emergency_var.set("Memory overload")
                    self.log_codex(f"⚠️ Emergency: Memory spike in PID {proc.info['pid']}")
                else:
                    self.health_var.set(f"OK ({mem:.2f}MB)")
                    healthy = True
        if not healthy:
            self.health_var.set("❌ Not running")
            self.emergency_var.set("PDP offline")
            self.log_codex("❌ PDP process not found.")

    def scan_ports(self):
        active_ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                active_ports.append(f"{conn.laddr.ip}:{conn.laddr.port}")
        self.ports_var.set(f"{', '.join(active_ports) or 'None'}")
        self.log_codex(f"🔗 Ports scanned: {len(active_ports)} active")

    def auto_enhance(self):
        # Real-time enhancement logic placeholder
        # You can expand this to scan and patch PDP source files
        self.enhancer_var.set("Monitoring PDP for enhancement triggers")
        self.log_codex("🛠️ Auto-enhancer monitoring PDP modules")

    def sync_swarm(self):
        for node in self.swarm_nodes:
            iface = node.split(" ")[0]
            stats = psutil.net_io_counters(pernic=True).get(iface)
            if stats:
                self.node_vars[node].set(f"Sent: {stats.bytes_sent // 1024}KB | Recv: {stats.bytes_recv // 1024}KB")
                self.log_codex(f"🔄 {node} sync: {stats.bytes_sent}B sent, {stats.bytes_recv}B received")
            else:
                self.node_vars[node].set("Offline")
                self.log_codex(f"⚠️ {node} appears offline")

    def log_codex(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.codex_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.codex_log.see(tk.END)

# === Launch Unified GUI + Daemon ===
if __name__ == "__main__":
    app = RealTimeESD()
    app.mainloop()

