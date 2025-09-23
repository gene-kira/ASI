# dominiondeck_launcher.py

import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("🔐 Elevation required. Relaunching as admin...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

import subprocess, importlib, socket, threading, signal, os, queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk
try:
    from ttkthemes import ThemedTk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkthemes"])
    from ttkthemes import ThemedTk

# ─── AUTLOADER ────────────────────────────────────────────────────────────────
required_libraries = {
    "dnslib": "dnslib",
    "cryptography": "cryptography",
}
def log_autoload(event, detail):
    with open("autoload.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z | {event} | {detail}\n")
def autoload_libraries(lib_map):
    for name, pip_name in lib_map.items():
        try:
            importlib.import_module(name)
            log_autoload("FOUND", name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            log_autoload("INSTALLED", pip_name)
autoload_libraries(required_libraries)

from dnslib import DNSRecord, RR, QTYPE, A

IP = '0.0.0.0'
PORT = 53
ZONE_FILE = 'zones.txt'
CACHE = {}
AGENTS = {
    "dns": "python dominiondeck_launcher.py --dns",
    "watchdog": "python dominiondeck_launcher.py --watchdog"
}
input_queue = queue.Queue()
output_queue = queue.Queue()

def log_event(role, event, detail):
    with open("trace.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z | [{role}] | {event} | {detail}\n")

def load_zone_file(path=ZONE_FILE):
    zones = {}
    if not os.path.exists(path): return zones
    with open(path) as f:
        for line in f:
            try:
                domain, rtype, ip = line.strip().split()
                zones[domain] = (rtype, ip)
            except: continue
    return zones

def mutate_zone(domain, new_ip, path=ZONE_FILE):
    lines, mutated = [], False
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    d, rtype, ip = line.strip().split()
                    if d == domain:
                        lines.append(f"{domain} {rtype} {new_ip}\n")
                        mutated = True
                    else:
                        lines.append(line)
                except: continue
    if not mutated:
        lines.append(f"{domain} A {new_ip}\n")
    with open(path, 'w') as f:
        f.writelines(lines)
    log_event("gui", "ZONE_MUTATE", f"{domain} → {new_ip}")

def dns_server():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    zones = load_zone_file()
    print(f"🧠 DNS server running on {IP}:{PORT}")
    while True:
        data, addr = sock.recvfrom(512)
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]
        log_event("dns", "QUERY", f"{qname} {qtype}")
        input_queue.put(f"{datetime.now().strftime('%H:%M:%S')} | {addr[0]} → {qname} [{qtype}]")
        cached = CACHE.get(qname)
        if cached:
            sock.sendto(cached, addr)
            log_event("dns", "CACHE_HIT", qname)
            output_queue.put(f"{datetime.now().strftime('%H:%M:%S')} | {qname} → CACHED")
            continue
        reply = request.reply()
        ip = zones.get(qname, ("A", "127.0.0.1"))[1]
        reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
        packed = reply.pack()
        CACHE[qname] = packed
        sock.sendto(packed, addr)
        log_event("dns", "RESPONSE", ip)
        output_queue.put(f"{datetime.now().strftime('%H:%M:%S')} | {qname} → {ip}")

def launch_agents():
    processes = {}
    for role, cmd in AGENTS.items():
        proc = subprocess.Popen(cmd, shell=True)
        processes[role] = proc
        log_event("launcher", "AGENT_LAUNCH", f"{role} PID={proc.pid}")
    return processes

def monitor_agents(processes):
    while True:
        for role, proc in processes.items():
            if proc.poll() is not None:
                log_event("watchdog", "RESPAWN", role)
                processes[role] = subprocess.Popen(AGENTS[role], shell=True)

def replay_trace():
    if not os.path.exists("trace.log"): return []
    with open("trace.log") as f:
        return f.readlines()

def launch_gui():
    root = ThemedTk(theme="equilux")
    root.title("DominionDeck Console")
    root.geometry("450x350")
    style = ttk.Style()
    style.configure("TLabel", font=("Consolas", 10))
    style.configure("TButton", font=("Consolas", 9), padding=4)

    ttk.Label(root, text="🧠 DNS DominionDeck", font=("Consolas", 12, "bold")).pack(pady=5)

    agent_frame = ttk.LabelFrame(root, text="Agents")
    agent_frame.pack(fill="x", padx=10, pady=5)
    for role in AGENTS:
        ttk.Label(agent_frame, text=f"🟢 {role}").pack(anchor="w")

    zone_frame = ttk.LabelFrame(root, text="Zone Mutation")
    zone_frame.pack(fill="x", padx=10, pady=5)
    domain_entry = ttk.Entry(zone_frame, width=25)
    domain_entry.pack(side="left", padx=5)
    ip_entry = ttk.Entry(zone_frame, width=15)
    ip_entry.pack(side="left", padx=5)
    ttk.Button(zone_frame, text="Mutate", command=lambda: mutate_zone(domain_entry.get(), ip_entry.get())).pack(side="left", padx=5)

    traffic_frame = ttk.LabelFrame(root, text="Live Traffic Monitor")
    traffic_frame.pack(fill="both", expand=True, padx=10, pady=5)
    input_box = tk.Text(traffic_frame, height=5, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
    input_box.pack(fill="x", padx=5, pady=2)
    input_box.insert(tk.END, "🧠 Input Traffic\n")
    output_box = tk.Text(traffic_frame, height=5, bg="#1e1e1e", fg="#00ffff", font=("Consolas", 9))
    output_box.pack(fill="x", padx=5, pady=2)
    output_box.insert(tk.END, "🧙 Output Traffic\n")

    trace_frame = ttk.LabelFrame(root, text="Trace Replay")
    trace_frame.pack(fill="both", expand=True, padx=10, pady=5)
    trace_box = tk.Text(trace_frame, height=5, bg="#1e1e1e", fg="#ffcc00", font=("Consolas", 9))
    trace_box.pack(fill="both", expand=True)
    ttk.Button(trace_frame, text="Replay Trace", command=lambda: [trace_box.delete("1.0", tk.END), [trace_box.insert(tk.END, line) for line in replay_trace()]]).pack(pady=2)

    def update_traffic():
        try:
            while not input_queue.empty():
                msg = input_queue.get()
                input_box.insert(tk.END, msg + "\n")
                input_box.see(tk.END)
            while not output_queue.empty():
                msg = output_queue.get()
                output_box.insert(tk.END, msg + "\n")
                output_box.see(tk.END)
        except: pass
        root.after(500, update_traffic)
    update_traffic()

    root.mainloop()

if __name__ == "__main__":
    if "--dns" in sys.argv:
        dns_server()
    elif "--watchdog" in sys.argv:
        monitor_agents(launch_agents())
    else:
        threading.Thread(target=lambda: subprocess.Popen([sys.executable, __file__, "--dns"]), daemon=True).start()
        threading.Thread(target=lambda: subprocess.Popen([sys.executable, __file__, "--watchdog"]), daemon=True).start()
        launch_gui()


   
