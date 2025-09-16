import tkinter as tk
from tkinter import scrolledtext
import subprocess
import datetime

def get_me_status():
    log = []
    version = "Unknown"
    amt_status = "Unknown"
    firewall_status = "Unchecked"

    try:
        bios = subprocess.check_output("wmic bios get smbiosbiosversion", shell=True).decode()
        version = bios.strip().split("\n")[-1]
        log.append(f"[{timestamp()}] ME BIOS version: {version}")
    except:
        log.append(f"[{timestamp()}] Failed to read BIOS version.")

    try:
        services = subprocess.check_output("sc query", shell=True).decode()
        if "LMS" in services:
            amt_status = "Detected"
        else:
            amt_status = "Not Found"
        log.append(f"[{timestamp()}] AMT service: {amt_status}")
    except:
        log.append(f"[{timestamp()}] Failed to query services.")

    try:
        rules = subprocess.check_output('netsh advfirewall firewall show rule name=all', shell=True).decode()
        if "Intel ME Block" in rules:
            firewall_status = "Blocked"
        else:
            firewall_status = "Open"
        log.append(f"[{timestamp()}] Firewall status: {firewall_status}")
    except:
        log.append(f"[{timestamp()}] Failed to check firewall rules.")

    return version, amt_status, firewall_status, log

def block_me_ports():
    ports_tcp = range(16992, 16996)
    ports_udp = [623, 664]
    for port in ports_tcp:
        subprocess.call(f'netsh advfirewall firewall add rule name="Intel ME Block TCP {port}" dir=out action=block protocol=TCP localport={port}', shell=True)
    for port in ports_udp:
        subprocess.call(f'netsh advfirewall firewall add rule name="Intel ME Block UDP {port}" dir=out action=block protocol=UDP localport={port}', shell=True)
    return f"[{timestamp()}] ME ports blocked. Comms nullified."

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def refresh_status():
    version, amt, fw, logs = get_me_status()
    version_var.set(version)
    amt_var.set(amt)
    fw_var.set(fw)
    log_box.delete(1.0, tk.END)
    for line in logs:
        log_box.insert(tk.END, line + "\n")

def block_ports():
    result = block_me_ports()
    log_box.insert(tk.END, result + "\n")

# GUI Setup
root = tk.Tk()
root.title("DominionDeck: ME Sentinel Console")
root.geometry("600x400")

tk.Label(root, text="Intel ME Status", font=("Arial", 16)).pack(pady=5)

frame = tk.Frame(root)
frame.pack()

version_var = tk.StringVar()
amt_var = tk.StringVar()
fw_var = tk.StringVar()

tk.Label(frame, text="ME Version:").grid(row=0, column=0, sticky="w")
tk.Label(frame, textvariable=version_var).grid(row=0, column=1, sticky="w")

tk.Label(frame, text="AMT Service:").grid(row=1, column=0, sticky="w")
tk.Label(frame, textvariable=amt_var).grid(row=1, column=1, sticky="w")

tk.Label(frame, text="Firewall:").grid(row=2, column=0, sticky="w")
tk.Label(frame, textvariable=fw_var).grid(row=2, column=1, sticky="w")

log_box = scrolledtext.ScrolledText(root, width=70, height=10)
log_box.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Refresh Status", command=refresh_status).pack(side="left", padx=10)
tk.Button(btn_frame, text="Block ME Ports", command=block_ports).pack(side="left", padx=10)

refresh_status()
root.mainloop()
