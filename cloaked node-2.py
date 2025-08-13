import tkinter as tk
from tkinter import ttk
import psutil
import subprocess
import random
import threading

# Mythic threat scoring logic
def score_threat(conn):
    score = 0
    if conn.status not in ("ESTABLISHED", "LISTEN"):
        score += 1
    if conn.raddr and conn.raddr.ip.startswith("192.168.") is False:
        score += 2
    if conn.pid is None:
        score += 2
    return score

# Real-time firewall block
def block_ip(ip):
    cmd = f'netsh advfirewall firewall add rule name="Block {ip}" dir=in action=block remoteip={ip}'
    subprocess.run(cmd, shell=True)

# Mythic mutation logic
def mutate_identity():
    fake_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))
    fake_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    return fake_mac, fake_ip

# GUI setup
root = tk.Tk()
root.title("🛡️ MagicBox Cloak Node — Real-Time Defense")
root.geometry("700x500")
root.configure(bg="#1e1e2f")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1e1e2f", foreground="white", font=("Consolas", 10))
style.configure("TButton", background="#2e2e3f", foreground="white", font=("Consolas", 10))
style.configure("TCombobox", fieldbackground="#2e2e3f", background="#2e2e3f", foreground="white")

title = ttk.Label(root, text="🧙 MagicBox Cloak Node", font=("Consolas", 16, "bold"))
title.pack(pady=10)

status_label = ttk.Label(root, text="Status: Idle")
status_label.pack()

mac_label = ttk.Label(root, text="MAC: --")
mac_label.pack()

ip_label = ttk.Label(root, text="IP: --")
ip_label.pack()

threat_box = tk.Text(root, height=15, width=80, bg="#12121c", fg="lime", font=("Consolas", 9))
threat_box.pack(pady=10)

interval_label = ttk.Label(root, text="Scan Interval (sec):")
interval_label.pack()

interval_var = tk.StringVar(value="5")
interval_dropdown = ttk.Combobox(root, textvariable=interval_var, values=["3", "5", "10", "30", "60"])
interval_dropdown.pack()

# Real-time scan loop
def scan_loop():
    status_label.config(text="Status: Scanning...")
    mac, ip = mutate_identity()
    mac_label.config(text=f"MAC: {mac}")
    ip_label.config(text=f"IP: {ip}")
    threat_box.delete("1.0", tk.END)

    conns = psutil.net_connections(kind='inet')
    for conn in conns:
        try:
            score = score_threat(conn)
            if score >= 3 and conn.raddr:
                ip = conn.raddr.ip
                threat_box.insert(tk.END, f"⚠️ Threat: {ip} | Score: {score}\n")
                block_ip(ip)
        except Exception as e:
            continue

    status_label.config(text="Status: Idle")
    interval = int(interval_var.get()) * 1000
    root.after(interval, scan_loop)

# Start button
def start_scan():
    scan_loop()

start_btn = ttk.Button(root, text="Start Real-Time Scan", command=start_scan)
start_btn.pack(pady=10)

root.mainloop()

