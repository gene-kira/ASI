import subprocess, sys, os, time, winreg, ctypes, hashlib, json, threading, tkinter as tk
from datetime import datetime

# === Auto-install required libs ===
for lib in ["psutil", "pywin32"]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# === Config ===
WATCHED = {
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection": {"AllowTelemetry": 0, "MaxTelemetryAllowed": 0},
    r"SYSTEM\CurrentControlSet\Services\DiagTrack": {"Start": 4}
}
SNAPSHOT_FILE = "codex_registry_snapshot.json"
LOG_FILE = "codex_mutation_log.txt"
CONSENT_FILE = "codex_consent.json"
PIPE = r"\\.\pipe\CodexPurgeGUI"
CONSENT = {k: False for k in ["registry_edit", "service_suppression", "snapshot_restore", "data_access"]}
QUEUE = []

# === Registry ===
def get_val(hive, path, name):
    try: return winreg.QueryValueEx(winreg.OpenKey(hive, path, 0, winreg.KEY_READ), name)[0]
    except: return None

def set_val(hive, path, name, val):
    if not CONSENT["registry_edit"]:
        QUEUE.append({"type": "registry_edit", "path": path, "name": name, "old": get_val(hive, path, name), "new": val, "timestamp": datetime.now().isoformat()})
        log("BLESSING_REQUIRED", f"{path}\\{name} → {val}")
        return
    try: winreg.SetValueEx(winreg.CreateKey(hive, path), name, 0, winreg.REG_DWORD, val)
    except Exception as e: log("ERROR", f"Set failed: {path}\\{name}: {e}")

# === Snapshot ===
def snapshot(): return {p: {n: get_val(winreg.HKEY_LOCAL_MACHINE if p.startswith("SYSTEM") else winreg.HKEY_CURRENT_USER, p, n) for n in v} for p, v in WATCHED.items()}
def hash_snap(snap): return hashlib.sha256(json.dumps(snap, sort_keys=True).encode()).hexdigest()
def restore(snap):
    if not CONSENT["snapshot_restore"]: return log("BLESSING_REQUIRED", "Restore blocked")
    for p, vals in snap.items():
        hive = winreg.HKEY_LOCAL_MACHINE if p.startswith("SYSTEM") else winreg.HKEY_CURRENT_USER
        for n, v in vals.items(): set_val(hive, p, n, v)

# === Logging ===
def log(t, msg):
    entry = f"[{datetime.now().isoformat()}] [{t}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(entry + "\n")
    try:
        with open(PIPE, "w", encoding="utf-8") as pipe:
            pipe.write(entry + "\n")
    except: pass

# === Watchdog ===
def watchdog():
    snap = snapshot()
    last_hash = hash_snap(snap)
    json.dump(snap, open(SNAPSHOT_FILE, "w", encoding="utf-8"))
    while True:
        current = snapshot()
        if hash_snap(current) != last_hash:
            log("MUTATION", "Detected")
            restore(snap)
            log("RESURRECTION", "Restored")
        else: log("HEARTBEAT", "Clean")
        time.sleep(10)

# === Elevation ===
def is_admin(): return ctypes.windll.shell32.IsUserAnAdmin()
def elevate(): ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join([f'"{a}"' for a in sys.argv]), None, 1)

# === GUI ===
class CodexGUI:
    def __init__(self, root):
        self.root = root
        root.title("Codex Purge Sentinel")
        root.geometry("800x700")
        root.configure(bg="#1e1e1e")

        self.status = tk.Label(root, text="Daemon Status: 🔄 Checking...", fg="white", bg="#1e1e1e", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.log_box = tk.Text(root, bg="#2e2e2e", fg="#00ff00", font=("Consolas", 12), height=12)
        self.log_box.pack(expand=True, fill="both", padx=10, pady=10)

        self.consent_panel()
        self.queue_panel()
        self.pipe_listener()
        self.heartbeat()

    def consent_panel(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(pady=5, fill="x", padx=10)
        tk.Label(frame, text="Consent Matrix", fg="white", bg="#1e1e1e", font=("Consolas", 12)).pack(anchor="w", padx=10)
        self.vars = {}
        for k in CONSENT:
            var = tk.BooleanVar(value=CONSENT[k])
            self.vars[k] = var
            tk.Checkbutton(frame, text=k, variable=var, bg="#1e1e1e", fg="white", selectcolor="#444444",
                           command=lambda key=k: self.update_consent(key)).pack(anchor="w", padx=20, pady=2)

    def update_consent(self, key):
        CONSENT[key] = self.vars[key].get()
        json.dump(CONSENT, open(CONSENT_FILE, "w", encoding="utf-8"))
        log("CONSENT_UPDATE", f"{key} → {CONSENT[key]}")

    def queue_panel(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(pady=5, fill="x", padx=10)
        tk.Label(frame, text="Blessing Queue", fg="white", bg="#1e1e1e", font=("Consolas", 12)).pack(anchor="w", padx=10)
        self.queue_box = tk.Text(frame, bg="#2e2e2e", fg="#ffcc00", font=("Consolas", 10), height=8)
        self.queue_box.pack(fill="x", padx=10)
        btns = tk.Frame(frame, bg="#1e1e1e")
        btns.pack(pady=5)
        tk.Button(btns, text="Approve All", command=self.approve_all, bg="#2e2e2e", fg="white").pack(side="left", padx=10)
        tk.Button(btns, text="Deny All", command=self.deny_all, bg="#2e2e2e", fg="white").pack(side="left", padx=10)
        self.refresh_queue()

    def refresh_queue(self):
        self.queue_box.delete("1.0", tk.END)
        for e in QUEUE:
            self.queue_box.insert(tk.END, f"{e['timestamp']} | {e['type']} | {e['path']}\\{e['name']} → {e['new']}\n")
        self.root.after(10000, self.refresh_queue)

    def approve_all(self):
        for e in QUEUE:
            hive = winreg.HKEY_LOCAL_MACHINE if e["path"].startswith("SYSTEM") else winreg.HKEY_CURRENT_USER
            try: winreg.SetValueEx(winreg.CreateKey(hive, e["path"]), e["name"], 0, winreg.REG_DWORD, e["new"])
            except Exception as ex: log("ERROR", f"Approve failed: {ex}")
        QUEUE.clear()
        log("BLESSING_APPROVED", "All mutations approved")

    def deny_all(self):
        QUEUE.clear()
        log("BLESSING_DENIED", "All mutations denied")

    def pipe_listener(self):
        def listen():
            if not os.path.exists(PIPE):
                try: os.mkfifo(PIPE)
                except: pass
            while True:
                try:
                    with open(PIPE, "r", encoding="utf-8") as pipe:
                        for line in pipe:
                            self.log_box.insert(tk.END, line)
                            self.log_box.see(tk.END)
                except: time.sleep(2)
        threading.Thread(target=listen, daemon=True).start()

    def heartbeat(self):
        def check():
            while True:
                time.sleep(15)
                self.status.config(text="Daemon Status: ✅ Running")
        threading.Thread(target=check, daemon=True).start()

# === Main ===
def main():
    if not is_admin(): return elevate()
    if os.path.exists(CONSENT_FILE):
        try: CONSENT.update(json.load(open(CONSENT_FILE, "r", encoding="utf-8")))
        except Exception as e: log("ERROR", f"Consent load failed: {e}")
    log("INIT", "Codex Purge Daemon initialized")
    threading.Thread(target=watchdog, daemon=True).start()
    root = tk.Tk()
    app = CodexGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

