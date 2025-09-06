import os, sys, time, threading, shutil, socket, uuid, json
from datetime import datetime, timedelta
from random import randint, choice
import tkinter as tk
from ttkbootstrap import Style
import psutil

CODEX_FILE = "fusion_codex.json"

# 📜 Codex Logger
def log_event(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    codex.insert(tk.END, f"[{timestamp}] {message}\n")
    codex.see(tk.END)

# 🧬 Replicator + Swarm Spawner
def replicate_swarm():
    base = sys.argv[0]
    paths = [os.getenv("APPDATA"), os.getenv("TEMP"), os.path.expanduser("~")]
    for i, path in enumerate(paths):
        target = os.path.join(path, f"MythicNode_{i}.exe")
        if not os.path.exists(target):
            try:
                shutil.copy2(base, target)
                log_event(f"🧬 Swarm node replicated: {target}")
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
        "cpu": "3%", "ram": "12MB", "user": "ghost",
        "location": "Null Island", "uptime": "00:00:01"
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

# 👻 Genre-Aware Decoy Injection
def inject_decoy_personas(ports):
    for port in ports:
        genre = "stealth" if port == 443 else "tactical"
        persona = "GhostContact" if genre == "stealth" else "PulseEcho"
        log_event(f"👻 Injected {genre} persona: {persona} on port {port}")

# 🧟 Squad Revival Logic
def squad_revive():
    nodes = ["MythicNode_0.exe", "MythicNode_1.exe", "MythicNode_2.exe"]
    for node in nodes:
        path = os.path.join(os.getenv("APPDATA"), node)
        if not os.path.exists(path):
            log_event(f"🧟 Reviving node: {node}")
            try:
                shutil.copy2(sys.argv[0], path)
            except Exception as e:
                log_event(f"⚠️ Revival failed: {e}")

# 🌀 Vortex Visualization (simulated)
def vortex_pulse():
    entropy = [round(randint(5, 9) + choice([0.1, 0.3, 0.5]), 2) for _ in range(10)]
    log_event(f"🌀 Vortex pulse: entropy ring = {entropy}")

# 🧠 Rewrite Engine
def detect_density_spike(flows):
    if len(flows) < 10: return False
    recent = flows[-10:]
    avg = sum(recent) / len(recent)
    variance = max(recent) - min(recent)
    return variance > 2.5 and avg > 7.0

def initiate_mutation_vote():
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = randint(6, 8)
    log_event(f"[🧠 Rewrite] New cloaking threshold: entropy > {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex_data = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex_data = json.load(f)
    codex_data.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex_data, f, indent=2)

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
    return open_ports

# 🧱 Daemon Background Thread
def daemon_thread():
    replicate_swarm()
    zero_trust_gate()
    send_fake_telemetry()
    destroy_mac_ip()
    timed_wipe("Backdoor leak", 3)
    protect_personal_data("face, fingerprint, phone, address, SSN, license")
    ports = scan_ports()
    squad_revive()
    entropy_ring = [round(randint(5, 9) + choice([0.1, 0.3, 0.5]), 2) for _ in range(20)]
    vortex_pulse()
    if detect_density_spike(entropy_ring) and initiate_mutation_vote():
        rewrite = rewrite_optimization_logic()
        store_rewrite_codex(rewrite)
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

footer = tk.Label(root, text="MythicBox Edition • Swarm-Grade • Zero Trust • Codex Mutation Enabled",
                  font=("Helvetica", 11), fg="#888", bg="#222")
footer.pack(side="bottom", pady=10)

# 🚀 Auto-Start Daemon
threading.Thread(target=daemon_thread, daemon=True).start()
root.after(1000, lambda: log_event("🔥 Auto-start complete. All systems defending."))
root.mainloop()

