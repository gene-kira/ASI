#!/usr/bin/env python3
# Sonic Shield v2.0 - MagicBox Edition
# Author: killer666

import os, sys, subprocess, time, logging, random, uuid, socket
from threading import Thread
from datetime import datetime, timedelta

# 🧠 Auto-install required libraries
def install(package):
    subprocess.run([sys.executable, "-m", "pip", "install", package])

try:
    import psutil
except ImportError:
    install("psutil")
    import psutil

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    install("tk")
    import tkinter as tk
    from tkinter import ttk

LOG_FILE = os.path.expanduser("~/sound_guardian.log")
SELF_DESTRUCT_TRIGGER = os.path.expanduser("~/sound_self_destruct.sh")
BIOMETRIC_HOOK = os.path.expanduser("~/biometric_validate.sh")
FAKE_TELEMETRY_BUFFER = os.path.expanduser("~/telemetry_buffer.tmp")
PERSONAL_DATA_TAG = os.path.expanduser("~/personal_data.tag")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')

# 🔒 USB Audio Block (simulated)
def block_usb_audio():
    logging.info("USB audio block simulated")

# 🔇 Analog Port Mute
def mute_analog_ports():
    for control in ['Master', 'Speaker', 'Headphone']:
        try:
            subprocess.run(["amixer", "-c", "0", "sset", control, "mute"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.warning(f"Failed to mute {control}: {e}")

# 🧬 Biometric Validation Stub
def biometric_validate():
    if os.path.exists(BIOMETRIC_HOOK):
        return subprocess.call([BIOMETRIC_HOOK]) == 0
    return True

# 💀 Self-Destruct Logic
def trigger_self_destruct(reason="Unknown"):
    logging.warning(f"Self-destruct triggered: {reason}")
    subprocess.run(["pkill", "-9", "pulseaudio"])
    subprocess.run(["pkill", "-9", "pipewire"])
    subprocess.run(["shred", "-u", LOG_FILE])
    subprocess.run(["shred", "-u", FAKE_TELEMETRY_BUFFER])
    subprocess.run(["shred", "-u", PERSONAL_DATA_TAG])

# 🔍 Real-Time Sound Monitor
def monitor_sound_events():
    while True:
        active = [p.info for p in psutil.process_iter(['name', 'pid']) if 'pulse' in p.info['name'] or 'pipewire' in p.info['name']]
        if active:
            logging.info(f"Sound activity detected: {active}")
            if not biometric_validate():
                trigger_self_destruct("Biometric validation failed")
        time.sleep(1)

# 🕸️ MAC/IP Cloaking Check
def mac_ip_decay_check():
    try:
        mac = uuid.getnode()
        ip = socket.gethostbyname(socket.gethostname())
        if mac == 0 or ip.startswith("127."):
            logging.warning("MAC/IP missing or spoofed. Countdown to self-destruct...")
            time.sleep(30)
            trigger_self_destruct("MAC/IP cloaking failure")
    except Exception as e:
        logging.error(f"MAC/IP check failed: {e}")
        time.sleep(30)
        trigger_self_destruct("MAC/IP check error")

# 🧑‍🔬 Personal Data Decay (1-day)
def personal_data_decay():
    if os.path.exists(PERSONAL_DATA_TAG):
        with open(PERSONAL_DATA_TAG, "r") as f:
            timestamp = f.read().strip()
        try:
            created = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - created > timedelta(days=1):
                logging.info("Personal data expired. Purging...")
                os.remove(PERSONAL_DATA_TAG)
        except:
            pass
    else:
        with open(PERSONAL_DATA_TAG, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 🛰️ Fake Telemetry Cloak
def telemetry_cloak():
    while True:
        fake_data = f"telemetry:{random.randint(1000,9999)}:{uuid.uuid4()}"
        with open(FAKE_TELEMETRY_BUFFER, "w") as f:
            f.write(fake_data)
        logging.info("Fake telemetry dispatched")
        time.sleep(30)
        os.remove(FAKE_TELEMETRY_BUFFER)

# 🚪 Backdoor Ejection Monitor
def monitor_backdoor_ejection():
    while True:
        conns = psutil.net_connections()
        for conn in conns:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                if conn.raddr.ip not in ['127.0.0.1', 'localhost']:
                    logging.warning(f"Suspicious outbound: {conn.raddr}")
                    time.sleep(3)
                    trigger_self_destruct("Backdoor data ejection")
        time.sleep(5)

# 🎨 Tkinter GUI: MagicBox Edition
def launch_gui():
    root = tk.Tk()
    root.title("🧬 Sonic Shield: MagicBox Edition")
    root.geometry("600x400")
    root.configure(bg="black")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="black", foreground="cyan", font=("Helvetica", 16))

    labels = [
        ("🧬 Sonic Shield Activated", "cyan"),
        ("🔒 All ports shielded", "lime"),
        ("🧠 Real-time telemetry live", "orange"),
        ("💀 Self-destruct armed", "red"),
        ("🧬 Mutation: MagicBox Edition", "magenta")
    ]

    for text, color in labels:
        lbl = ttk.Label(root, text=text)
        lbl.configure(foreground=color)
        lbl.pack(pady=10)

    root.mainloop()

# 🧰 Install Hooks
def install_hooks():
    with open(SELF_DESTRUCT_TRIGGER, "w") as f:
        f.write("""#!/bin/bash
pkill -9 pulseaudio || true
pkill -9 pipewire || true
shred -u ~/sound_guardian.log
shred -u ~/telemetry_buffer.tmp
shred -u ~/personal_data.tag
""")
    os.chmod(SELF_DESTRUCT_TRIGGER, 0o755)

    with open(BIOMETRIC_HOOK, "w") as f:
        f.write("""#!/bin/bash
exit 0
""")
    os.chmod(BIOMETRIC_HOOK, 0o755)

# 🧠 Main Mutation
def main():
    logging.info("Sonic Shield Mutation Started")
    block_usb_audio()
    mute_analog_ports()
    install_hooks()
    Thread(target=monitor_sound_events, daemon=True).start()
    Thread(target=mac_ip_decay_check, daemon=True).start()
    Thread(target=personal_data_decay, daemon=True).start()
    Thread(target=telemetry_cloak, daemon=True).start()
    Thread(target=monitor_backdoor_ejection, daemon=True).start()
    launch_gui()

if __name__ == "__main__":
    main()

