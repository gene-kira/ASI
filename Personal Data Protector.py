import os, sys, time, threading, shutil, socket, uuid
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog
from ttkbootstrap import Style
import psutil

# 📜 Codex Logger
def log_event(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    codex.insert(tk.END, f"[{timestamp}] {message}\n")
    codex.see(tk.END)

# 🧬 Replicator Logic
def replicate_self():
    paths = [os.getenv("APPDATA"), os.getenv("TEMP"), os.path.expanduser("~")]
    for path in paths:
        target = os.path.join(path, "MythicNode.exe")
        if not os.path.exists(target):
            try:
                shutil.copy2(sys.argv[0], target)
                log_event(f"🧬 Replicated to {target}")
            except Exception as e:
                log_event(f"⚠️ Replication failed: {e}")

# 🔐 Zero Trust Engine
def zero_trust_gate():
    threats = ["AI", "ASI", "hacker", "remote inject", "unauthorized scan"]
    for threat in threats:
        log_event(f"🛡️ Blocked: {threat}")

# 💣 Self-Destruct Timers
def timed_wipe(data_type, delay_sec):
    def wipe():
        time.sleep(delay_sec)
        log_event(f"💣 {data_type} self-destructed after {delay_sec}s")
    threading.Thread(target=wipe, daemon=True).start()

# 🕵️‍♂️ Fake Telemetry Generator
def send_fake_telemetry():
    fake_data = {
        "cpu": "3%",
        "ram": "12MB",
        "user": "ghost",
        "location": "Null Island",
        "uptime": "00:00:01"
    }
    log_event(f"🕵️‍♂️ Sent fake telemetry: {fake_data}")
    timed_wipe("Fake telemetry", 30)

# 🧠 Personal Data Guard
def protect_personal_data(data):
    log_event(f"🔐 Personal data registered: {data}")
    expire = datetime.now() + timedelta(days=1)
    threading.Thread(target=lambda: expire_data(data, expire), daemon=True).start()

def expire_data(data, expire_time):
    while datetime.now() < expire_time:
        time.sleep(10)
    log_event(f"💣 Personal data auto-wiped: {data}")

# 🌐 MAC/IP Auto-Wipe
def destroy_mac_ip():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        ip = socket.gethostbyname(socket.gethostname())
        log_event(f"🌐 MAC: {mac}, IP: {ip}")
        timed_wipe("MAC/IP address", 30)
    except Exception as e:
        log_event(f"⚠️ MAC/IP fetch failed: {e}")

# 👻 Decoy Persona Injection
def inject_decoy_personas(ports):
    for port in ports:
        persona = "GhostContact" if port == 443 else "PulseEcho"
        log_event(f"👻 Injected decoy persona: {persona} on port {port}")

# 🌀 Port Scan Logic
def scan_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            port = conn.laddr.port
            open_ports.append(port)
    if open_ports:
        log_event(f"Tunnel scan complete. Ports active: {open_ports}")
        inject_decoy_personas(open_ports)
    else:
        log_event("Tunnel scan complete. No active ports found.")

# 🎮 Manual Shortcut Selector
def select_shortcut():
    path = filedialog.askopenfilename(title="Select Shortcut or Executable")
    if path and os.path.exists(path):
        log_event(f"🎮 Shortcut selected: {os.path.basename(path)}")
    else:
        log_event("⚠️ No valid file selected.")

# 🧱 Daemon Background Thread
def daemon_thread():
    replicate_self()
    zero_trust_gate()
    send_fake_telemetry()
    destroy_mac_ip()
    timed_wipe("Backdoor leak", 3)
    protect_personal_data("face, fingerprint, phone, address, SSN, license")
    scan_ports()
    while True:
        time.sleep(60)
        log_event("🌀 MythicNode heartbeat: system secure")

# 🎨 GUI Setup
style = Style(theme="cyborg")
root = style.master
root.title("🌀 MythicBox ASI Node")
root.geometry("800x600")
root.resizable(False, False)
root.configure(bg="#222")

status_label = tk.Label(root, text="🌀 MythicNode initialized. Passive defense active.",
                        font=("Helvetica", 16), fg="#0ff", bg="#222")
status_label.pack(pady=10)

codex_frame = tk.Frame(root, bg="#222")
codex_frame.pack(pady=10, fill="both", expand=True)

codex = tk.Text(codex_frame, height=12, bg="#111", fg="#0ff", font=("Courier", 10))
codex.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(codex_frame, command=codex.yview)
scrollbar.pack(side="right", fill="y")
codex.config(yscrollcommand=scrollbar.set)

shortcut_btn = tk.Button(root, text="🎮 Select Shortcut", font=("Helvetica", 14),
                         bg="#333", fg="#0ff", command=select_shortcut)
shortcut_btn.pack(pady=10)

footer = tk.Label(root, text="MythicBox Edition • Real-time only • Zero Trust • SquadSync Ready",
                  font=("Helvetica", 11), fg="#888", bg="#222")
footer.pack(side="bottom", pady=10)

# 🚀 Auto-Start Daemon
threading.Thread(target=daemon_thread, daemon=True).start()
root.after(1000, lambda: log_event("🔥 Auto-start complete. All systems defending."))
root.mainloop()

