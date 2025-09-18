#!/usr/bin/env python3
import subprocess, time, threading, logging, sys
from datetime import datetime
from tkinter import *
from tkinter import ttk

# 🧠 CONFIG
LOG_FILE = "cpu_gui_mutator.log"
LOW_THRESHOLD = 20
HIGH_THRESHOLD = 85

# 🛠️ AUTO-INSTALL
def ensure_dependencies():
    try:
        import psutil
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
ensure_dependencies()
import psutil

# 🧾 LOGGING
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s')

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd}\n{e}")
        return None

def get_governor():
    return run("cpufreq-info -p | awk '{print $3}'")

def set_governor(gov):
    run(f"sudo cpufreq-set -g {gov}")
    log_mutation("Governor", gov)

def toggle_turbo(state):
    run(f"echo {1 if state == 'on' else 0} | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo")
    log_mutation("Turbo Boost", state)

def log_mutation(label, value):
    timestamp = datetime.now().isoformat()
    logging.info(f"🔁 Mutation: {label} → {value} @ {timestamp}")

# 🖥️ GUI SETUP
class CPUGUI:
    def __init__(self, root):
        self.root = root
        root.title("🧓 CPU Control Shell")
        root.geometry("400x300")
        self.create_widgets()
        self.update_loop()

    def create_widgets(self):
        self.usage_label = Label(self.root, text="CPU Usage: --%", font=("Arial", 14))
        self.usage_label.pack(pady=10)

        self.freq_label = Label(self.root, text="Frequency: -- MHz", font=("Arial", 14))
        self.freq_label.pack(pady=10)

        self.gov_label = Label(self.root, text="Governor: --", font=("Arial", 12))
        self.gov_label.pack(pady=5)

        self.gov_frame = Frame(self.root)
        self.gov_frame.pack(pady=5)
        for gov in ["performance", "powersave", "ondemand", "userspace"]:
            Button(self.gov_frame, text=gov, command=lambda g=gov: set_governor(g)).pack(side=LEFT, padx=5)

        self.turbo_frame = Frame(self.root)
        self.turbo_frame.pack(pady=10)
        Button(self.turbo_frame, text="Turbo ON", command=lambda: toggle_turbo("on")).pack(side=LEFT, padx=5)
        Button(self.turbo_frame, text="Turbo OFF", command=lambda: toggle_turbo("off")).pack(side=LEFT, padx=5)

        self.log_box = Text(self.root, height=6, width=45)
        self.log_box.pack(pady=10)

    def update_loop(self):
        usage = psutil.cpu_percent(interval=1)
        freq = run("cpufreq-info -f")
        gov = get_governor()

        self.usage_label.config(text=f"CPU Usage: {usage:.1f}%")
        self.freq_label.config(text=f"Frequency: {freq} MHz" if freq else "Frequency: --")
        self.gov_label.config(text=f"Governor: {gov}" if gov else "Governor: --")

        if usage < LOW_THRESHOLD and gov != "powersave":
            set_governor("powersave")
            toggle_turbo("off")
            self.log_box.insert(END, f"🧬 Low Load → powersave @ {usage:.1f}%\n")
        elif usage > HIGH_THRESHOLD and gov != "performance":
            set_governor("performance")
            toggle_turbo("on")
            self.log_box.insert(END, f"🔥 High Load → performance @ {usage:.1f}%\n")

        self.root.after(5000, self.update_loop)

# 🚀 LAUNCH
if __name__ == "__main__":
    root = Tk()
    app = CPUGUI(root)
    root.mainloop()
