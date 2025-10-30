import socket, threading, time, random, platform, subprocess, sys, ctypes, os
from tkinter import Tk, Label, Frame, StringVar, Button, OptionMenu
from datetime import datetime

# === CONFIG ===
ROTATION_OPTIONS = {
    "30 minutes": 1800,
    "1 hour": 3600,
    "6 hours": 21600
}
ROTATION_COUNT = 5
TOTAL_PORTS = list(range(1024, 65535))
open_ports = []
sockets = []
firewall_active = False
rotation_interval = ROTATION_OPTIONS["30 minutes"]

# === GUI VARIABLES ===
root = None
port_label = None
status_label = None
interval_var = None
toggle_button = None

# === DEBUG LOGGING ===
def log_startup():
    try:
        elevated = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        elevated = False
    print(f"[Codex Sentinel] PID {os.getpid()} launched. Elevated: {elevated}")

# === ELEVATION CHECK ===
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("[Codex Sentinel] Elevation required. Relaunching as administrator...")
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        sys.exit()

# === PORT BINDING ===
def bind_port(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(5)
        return s
    except:
        return None

# === CLOAKING (Linux only) ===
def cloak_ports():
    if platform.system() == "Linux":
        subprocess.call(["iptables", "-F"])
        subprocess.call(["iptables", "-P", "INPUT", "DROP"])
        for port in open_ports:
            subprocess.call(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"])

# === ROTATION ENGINE ===
def rotate_ports():
    global open_ports, sockets
    while True:
        if firewall_active:
            for s in sockets:
                try: s.close()
                except: pass
            open_ports = random.sample(TOTAL_PORTS, ROTATION_COUNT)
            sockets = []
            for p in open_ports:
                s = bind_port(p)
                if s: sockets.append(s)
            cloak_ports()
        time.sleep(rotation_interval)

# === GUI OVERLAY ===
def launch_gui():
    global root, port_label, status_label, interval_var, toggle_button
    root = Tk()
    root.title("Codex Sentinel Shell")
    root.geometry("400x250")

    Frame(root).pack()
    port_label = StringVar()
    status_label = StringVar()
    interval_var = StringVar(value="30 minutes")

    Label(root, textvariable=port_label, font=("Consolas", 12)).pack(pady=5)
    Label(root, textvariable=status_label, font=("Consolas", 10)).pack(pady=5)

    OptionMenu(root, interval_var, *ROTATION_OPTIONS.keys(), command=update_interval).pack(pady=5)
    toggle_button = Button(root, text="Start Firewall", command=toggle_firewall)
    toggle_button.pack(pady=10)

    refresh_gui()
    root.mainloop()

def refresh_gui():
    if port_label and status_label:
        port_label.set(f"Open Ports: {open_ports}\nUpdated: {datetime.now().strftime('%H:%M:%S')}")
        status = "ACTIVE" if firewall_active else "INACTIVE"
        status_label.set(f"Firewall Status: {status}")
    root.after(1000, refresh_gui)

def toggle_firewall():
    global firewall_active
    firewall_active = not firewall_active
    if toggle_button:
        toggle_button.config(text="Stop Firewall" if firewall_active else "Start Firewall")

def update_interval(selection):
    global rotation_interval
    rotation_interval = ROTATION_OPTIONS.get(selection, 1800)
    print(f"[Codex Sentinel] Rotation interval set to {selection} ({rotation_interval} seconds)")

# === THREAT DETECTION STUB ===
def threat_daemon():
    while True:
        time.sleep(60)

# === COUNTRY FILTER STUB ===
def country_filter():
    pass

# === SWARM SYNC STUB ===
def swarm_sync():
    pass

# === MAIN DAEMON ===
def start_firewall():
    log_startup()
    if platform.system() == "Windows":
        ensure_admin()
    threading.Thread(target=rotate_ports, daemon=True).start()
    threading.Thread(target=threat_daemon, daemon=True).start()
    threading.Thread(target=swarm_sync, daemon=True).start()
    launch_gui()

if __name__ == "__main__":
    start_firewall()

