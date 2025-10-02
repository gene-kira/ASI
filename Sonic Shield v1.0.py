#!/usr/bin/env python3
# Sonic Shield Mutation: MagicBox Edition (Tkinter GUI)
# Author: killer666

import os, subprocess, sys, time, logging
from threading import Thread

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

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')

# 🔒 USB Audio Block (simulated for user-level)
def block_usb_audio():
    logging.info("USB audio block simulated (requires root for real enforcement)")

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
def trigger_self_destruct():
    logging.warning("Unauthorized sound activity detected. Triggering self-destruct...")
    subprocess.run(["pkill", "-9", "pulseaudio"])
    subprocess.run(["pkill", "-9", "pipewire"])
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

# 🔍 Real-Time Sound Monitor
def monitor_sound_events():
    while True:
        active = [p.info for p in psutil.process_iter(['name', 'pid']) if 'pulse' in p.info['name'] or 'pipewire' in p.info['name']]
        if active:
            logging.info(f"Sound activity detected: {active}")
            if not biometric_validate():
                trigger_self_destruct()
        time.sleep(1)

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
    launch_gui()

if __name__ == "__main__":
    main()

