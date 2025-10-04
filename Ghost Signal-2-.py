import socket, psutil, threading, tkinter as tk
from tkinter import ttk
import pyttsx3, time, datetime, os, random

# 🔊 Voice Engine Setup
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# 🎨 GUI Setup
root = tk.Tk()
root.title("🧠 Mythic Deep Scanner - MagicBox")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", rowheight=25)
style.map("Treeview", background=[('selected', '#007acc')])

tree = ttk.Treeview(root, columns=("Port", "Status", "Process", "Entropy", "Timestamp"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True)

log_box = tk.Text(root, height=10, bg="#252526", fg="white", font=("Consolas", 10))
log_box.pack(fill=tk.X)

# 🎙️ Speak Alert
def speak(text):
    engine.say(text)
    engine.runAndWait()

# 🧠 Log Mutation
def log_event(message, severity="info"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    tag = "⚠️" if severity == "warn" else "🧠"
    log_box.insert(tk.END, f"[{timestamp}] {tag} {message}\n")
    log_box.see(tk.END)
    speak(message)

# 🔐 Self-Destruct Logic
def self_destruct():
    log_event("🔥 Tampering detected. Initiating self-destruct protocol.", "warn")
    speak("System breach. Purging sensitive memory.")
    for i in range(5):
        log_event(f"Purging memory block {i+1}/5...", "warn")
        time.sleep(0.5)
    os._exit(1)

# ❤️ Biometric Hook (Simulated Heartbeat)
def heartbeat_check():
    while True:
        bpm = random.randint(55, 95)
        if bpm < 50 or bpm > 120:
            log_event(f"💓 Biometric anomaly: Heartbeat {bpm} BPM", "warn")
        time.sleep(10)

# 🧬 Entropy Estimator
def estimate_entropy(port):
    return round(random.uniform(0.1, 1.0), 2)

# 🕸️ Swarm Sync (Simulated)
def swarm_sync(port, status):
    log_event(f"🕸️ Swarm sync: Port {port} status '{status}' validated across 3 nodes.")

# 🔍 Scan Ports + Processes
def scan_ports():
    seen_ports = set()
    while True:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            laddr = conn.laddr.port if conn.laddr else None
            pid = conn.pid
            status = conn.status
            if laddr and laddr not in seen_ports:
                seen_ports.add(laddr)
                proc_name = "Unknown"
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                except:
                    pass
                entropy = estimate_entropy(laddr)
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                tree.insert("", "end", values=(laddr, status, proc_name, entropy, timestamp))
                if status not in ("LISTEN", "ESTABLISHED") or entropy > 0.8:
                    log_event(f"Port {laddr} anomaly: {status}, entropy {entropy} via {proc_name}", "warn")
                    swarm_sync(laddr, status)
                    if entropy > 0.95:
                        self_destruct()
        time.sleep(5)

# 🧪 File Mutation Watchdog (Simulated)
def file_watchdog():
    watched = ["config.txt", "secrets.env", "guardian.log"]
    while True:
        for file in watched:
            if os.path.exists(file):
                size = os.path.getsize(file)
                if size > 100000:
                    log_event(f"📁 File anomaly: {file} size {size} bytes", "warn")
        time.sleep(15)

# 🚀 Launch Threads
threading.Thread(target=scan_ports, daemon=True).start()
threading.Thread(target=heartbeat_check, daemon=True).start()
threading.Thread(target=file_watchdog, daemon=True).start()

# 🧙‍♂️ Start GUI
log_event("🧠 Mythic Scanner initialized. Monitoring all ports, processes, and mutations...")
root.mainloop()

