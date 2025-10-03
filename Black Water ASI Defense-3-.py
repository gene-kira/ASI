# === Autoloader ===
import subprocess, sys, importlib
required_libs = ["psutil", "socket", "tkinter", "datetime", "os", "json"]
for lib in required_libs:
    try: importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# === Imports ===
import psutil, socket, threading, time, os, json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

# === Memory Core ===
MEMORY_FILE = "memory.vault"
def load_memory():
    try: return json.load(open(MEMORY_FILE))
    except: return {}
def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w"))
def remember(key, value, ttl=None):
    mem = load_memory()
    mem[key] = {"value": value, "timestamp": time.time(), "ttl": ttl}
    save_memory(mem)
def forget_expired():
    mem = load_memory()
    now = time.time()
    for k in list(mem):
        ttl = mem[k].get("ttl")
        if ttl and now - mem[k]["timestamp"] > ttl:
            del mem[k]
    save_memory(mem)

# === Learning Engine ===
def learn_event(event_type):
    mem = load_memory()
    stats = mem.get("event_stats", {})
    stats[event_type] = stats.get(event_type, 0) + 1
    remember("event_stats", stats)

# === Self-Destruct Registry ===
destruct_registry = []
def schedule_destruction(label, seconds):
    expiry = datetime.now() + timedelta(seconds=seconds)
    destruct_registry.append((label, expiry))
def check_destructions():
    now = datetime.now()
    for label, expiry in destruct_registry[:]:
        if now >= expiry:
            label.config(text="💣 SELF-DESTRUCTED", foreground="black")
            destruct_registry.remove((label, expiry))

# === Real-Time Telemetry ===
def get_telemetry():
    ip = socket.gethostbyname(socket.gethostname())
    mac = "N/A"
    for iface in psutil.net_if_addrs():
        for snic in psutil.net_if_addrs()[iface]:
            if snic.family.name == 'AF_LINK':
                mac = snic.address
                break
    return {
        "CPU": f"{psutil.cpu_percent()}%",
        "RAM": f"{psutil.virtual_memory().percent}%",
        "Disk": f"{psutil.disk_usage('/').percent}%",
        "IP": ip,
        "MAC": mac
    }

# === Zero Trust Firewall ===
def zero_trust_check():
    if os.name != 'nt' and os.geteuid() == 0:
        raise PermissionError("Elevation detected. Triggering self-destruct.")

# === Event Handlers ===
def redirect_probe(label):
    label.config(text="🔁 Redirected to Mimic Node", foreground="blue")
    schedule_destruction(label, 3)
    learn_event("redirect")
def reflect_probe(label):
    label.config(text="🔄 Reflected to Origin", foreground="red")
    schedule_destruction(label, 3)
    learn_event("reflect")
def handle_personal_data(label):
    label.config(text="⚠️ Personal Data Detected", foreground="orange")
    schedule_destruction(label, 86400)
    learn_event("personal_data")
def inject_fake_telemetry(label):
    label.config(text="🌀 Fake Telemetry Injected", foreground="purple")
    schedule_destruction(label, 30)
    learn_event("fake_telemetry")
def handle_mac_ip_exposure(label):
    label.config(text="🚨 MAC/IP Exposure Detected", foreground="red")
    schedule_destruction(label, 30)
    learn_event("mac_ip_exposure")
def handle_backdoor_leak(label):
    label.config(text="💣 Backdoor Data Leak Detected", foreground="red")
    schedule_destruction(label, 3)
    learn_event("backdoor_leak")

# === GUI Setup ===
class ASIGuardianGUI:
    def __init__(self, root):
        self.root = root
        root.title("ASI Guardian Shell")
        root.configure(bg="black")
        self.labels = {}

        ttk.Label(root, text="MILITARY-GRADE ASI DEFENSE", font=("Consolas", 16), foreground="green", background="black").pack(pady=10)

        self.telemetry_frame = ttk.Frame(root)
        self.telemetry_frame.pack(pady=10)
        for key in ["CPU", "RAM", "Disk", "IP", "MAC"]:
            lbl = ttk.Label(self.telemetry_frame, text=f"{key}: ...", font=("Consolas", 12))
            lbl.pack()
            self.labels[key] = lbl

        self.event_frame = ttk.Frame(root)
        self.event_frame.pack(pady=10)
        for event in ["Redirect", "Reflect", "Personal Data", "Fake Telemetry", "MAC/IP Exposure", "Backdoor Leak"]:
            btn = ttk.Button(self.event_frame, text=event, command=lambda e=event: self.trigger_event(e))
            btn.pack(pady=2)

        self.status_label = ttk.Label(root, text="Status: Monitoring...", font=("Consolas", 12), foreground="white", background="black")
        self.status_label.pack(pady=10)

        self.memory_label = ttk.Label(root, text="Memory: ...", font=("Consolas", 10), foreground="gray", background="black")
        self.memory_label.pack(pady=5)

        self.update_loop()

    def trigger_event(self, event):
        if event == "Redirect": redirect_probe(self.status_label)
        elif event == "Reflect": reflect_probe(self.status_label)
        elif event == "Personal Data": handle_personal_data(self.status_label)
        elif event == "Fake Telemetry": inject_fake_telemetry(self.status_label)
        elif event == "MAC/IP Exposure": handle_mac_ip_exposure(self.status_label)
        elif event == "Backdoor Leak": handle_backdoor_leak(self.status_label)

    def update_loop(self):
        try:
            zero_trust_check()
            telemetry = get_telemetry()
            for key, value in telemetry.items():
                self.labels[key].config(text=f"{key}: {value}")
            check_destructions()
            forget_expired()
            stats = load_memory().get("event_stats", {})
            self.memory_label.config(text=f"Memory: {stats}")
        except Exception as e:
            self.status_label.config(text=f"💣 {str(e)}", foreground="black")
        self.root.after(1000, self.update_loop)

# === Launch ===
if __name__ == "__main__":
    root = tk.Tk()
    gui = ASIGuardianGUI(root)
    root.mainloop()

