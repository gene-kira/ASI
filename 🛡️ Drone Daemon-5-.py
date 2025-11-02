import os, sys, platform

# 🔺 Elevation Check (Windows only)
def is_admin():
    try: return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

if not is_admin():
    if platform.system() == "Windows":
        import ctypes
        script = os.path.abspath(sys.argv[0])
        params = " ".join(sys.argv[1:] + ["--elevated"])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            print("[🔺] Relaunching with admin rights...")
        except Exception as e:
            print(f"[❌] Elevation failed: {e}")
        sys.exit()
elif "--elevated" in sys.argv:
    print("[✅] Running with elevated privileges.")

import subprocess, socket, json, time, threading, psutil, winreg, tkinter as tk
from tkinter import ttk
from collections import defaultdict

# 🧬 Autoloader
for lib in ["psutil", "json", "time", "threading", "socket", "tkinter", "winreg", "collections"]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🔗 Socket Server
class DroneDaemon:
    def __init__(self, port=5050): self.clients, self.port = [], port
    def start(self): threading.Thread(target=self._accept, daemon=True).start()
    def _accept(self):
        s = socket.socket(); s.bind(("localhost", self.port)); s.listen()
        while True: self.clients.append(s.accept()[0])
    def send(self, event):
        msg = json.dumps(event) + "\n"
        for c in self.clients[:]:
            try: c.sendall(msg.encode())
            except: self.clients.remove(c)

# 🧠 Registry Monitor
class RegistryMonitor:
    def __init__(self, daemon, keys, lock_path="drone_lock.json"):
        self.d, self.k = daemon, keys
        self.h, self.v, self.pre = defaultdict(list), {}, self._snap()
        self.lock = json.load(open(lock_path)) if os.path.exists(lock_path) else {}

    def read(self, p, n):
        try: return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p), n)[0]
        except: return None

    def write(self, p, n, v, t):
        try: winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p, 0, winreg.KEY_SET_VALUE), n, 0, getattr(winreg, t), v)
        except: pass

    def _snap(self): return {f"{p}\\{n}": self.read(p, n) for p, n in self.k}

    def _flip(self, k, v):
        now = time.time(); self.h[k].append((now, v))
        self.h[k] = [(t, val) for t, val in self.h[k] if now - t <= 10]
        if len(set(val for _, val in self.h[k])) > 1 and len(self.h[k]) >= 3:
            self.d.send({"type": "flipflop", "setting": k, "status": "⚠️ Flipping", "flips": len(self.h[k])})

    def monitor(self):
        while True:
            for p, n in self.k:
                k = f"{p}\\{n}"; v = self.read(p, n)
                if v != self.v.get(k): self._flip(k, v); self.v[k] = v
            time.sleep(2)

    def mutation_loop(self):
        while True:
            post = self._snap()
            for k in self.pre:
                if k in post and self.pre[k] != post[k]:
                    self.d.send({"type": "mutation", "setting": k, "old": self.pre[k], "new": post[k], "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
            self.pre = post.copy(); time.sleep(30)

    def lock_loop(self):
        while True:
            for k, info in self.lock.items():
                p, n = k.rsplit("\\", 1); cur = self.read(p, n)
                if cur != info["value"]:
                    self.d.send({"type": "lock", "setting": k, "expected": info["value"], "actual": cur, "restored": info.get("restore", False), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})
                    if info.get("restore"): self.write(p, n, info["value"], info["type"])
            time.sleep(10)

# 🔗 Connection Tracker
def track_connections(d):
    while True:
        for c in psutil.net_connections(kind='inet'):
            if c.status == 'ESTABLISHED':
                pid = c.pid; proc = psutil.Process(pid).name() if pid else "Unknown"
                remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "N/A"
                d.send({"type": "connection", "process": proc, "pid": pid, "remote": remote})
        time.sleep(10)

# 🧙 GUI Console
class DroneGUI:
    def __init__(self, root):
        root.title("DRONE: ASI Oversight Console"); root.configure(bg="#0f0f0f"); root.geometry("1000x800")
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="#00ffff", fieldbackground="#1a1a1a", font=("Consolas", 10))
        self.panels = {
            "flipflop": self._panel(root, "🧠 Flip-Flop Matrix", ["Setting", "Status", "Flips"]),
            "connection": self._panel(root, "🔗 Connection Tracker", ["Process", "PID", "Remote"]),
            "mutation": self._panel(root, "🧬 Mutation Log", ["Setting", "Old", "New", "Timestamp"]),
            "lock": self._panel(root, "🔐 Lock Status", ["Setting", "Expected", "Actual", "Restored", "Timestamp"])
        }
        threading.Thread(target=self._socket_client, daemon=True).start()

    def _panel(self, root, title, cols):
        ttk.Label(root, text=title).pack(anchor="w", padx=10, pady=(10, 0))
        frame = tk.Frame(root, bg="#1a1a1a", bd=2, relief="groove"); frame.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=6)
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
        tree.pack(fill="both", expand=True); return tree

    def _socket_client(self, port=5050):
        while True:
            try:
                client = socket.socket(); client.connect(("localhost", port)); buf = ""
                while True:
                    buf += client.recv(1024).decode()
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1); self._event(json.loads(line))
            except: time.sleep(2)

    def _event(self, e):
        if e["type"] == "flipflop":
            self.panels["flipflop"].insert("", "end", values=(e["setting"], e["status"], e["flips"]))
        elif e["type"] == "connection":
            self.panels["connection"].insert("", "end", values=(e["process"], e["pid"], e["remote"]))
        elif e["type"] == "mutation":
            self.panels["mutation"].insert("", "end", values=(e["setting"], e["old"], e["new"], e["timestamp"]))
        elif e["type"] == "lock":
            self.panels["lock"].insert("", "end", values=(e["setting"], e["expected"], e["actual"], "🔄 Restored" if e["restored"] else "⚠️ Alert", e["timestamp"]))

# 🚀 Launch
if __name__ == "__main__":
    daemon = DroneDaemon(); daemon.start()
    keys = [
        ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection", "AllowTelemetry"),
        ("SYSTEM\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy\\StandardProfile", "EnableFirewall"),
        ("SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters", "MaxCacheTtl")
    ]
    monitor = RegistryMonitor(daemon, keys)
    threading.Thread(target=monitor.monitor, daemon=True).start()
    threading.Thread(target=monitor.mutation_loop, daemon=True).start()
    threading.Thread(target=monitor.lock_loop, daemon=True).start()
    root = tk.Tk()
    DroneGUI(root)
    root.mainloop()


