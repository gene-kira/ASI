import socket
import psutil
import threading
import tkinter as tk
from tkinter import ttk
import pyttsx3
import time
import datetime

# 🔊 Voice Engine Setup
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# 🎨 GUI Setup
root = tk.Tk()
root.title("🧠 Deep Port Scanner - MagicBox")
root.geometry("800x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", rowheight=25)
style.map("Treeview", background=[('selected', '#007acc')])

tree = ttk.Treeview(root, columns=("Port", "Status", "Process", "Timestamp"), show="headings")
tree.heading("Port", text="Port")
tree.heading("Status", text="Status")
tree.heading("Process", text="Process")
tree.heading("Timestamp", text="Timestamp")
tree.pack(fill=tk.BOTH, expand=True)

log_box = tk.Text(root, height=8, bg="#252526", fg="white", font=("Consolas", 10))
log_box.pack(fill=tk.X)

# 🎙️ Speak Alert
def speak(text):
    engine.say(text)
    engine.runAndWait()

# 🧠 Log Mutation
def log_event(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{timestamp}] {message}\n")
    log_box.see(tk.END)
    speak(message)

# 🔍 Scan Ports
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
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                tree.insert("", "end", values=(laddr, status, proc_name, timestamp))
                if status not in ("LISTEN", "ESTABLISHED"):
                    log_event(f"⚠️ Port {laddr} anomaly: {status} via {proc_name}")
        time.sleep(5)

# 🚀 Launch Scanner Thread
threading.Thread(target=scan_ports, daemon=True).start()

# 🧙‍♂️ Start GUI
log_event("🧠 Deep Scanner initialized. Monitoring all ports...")
root.mainloop()

