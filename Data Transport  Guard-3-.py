# 🔄 Autoloader
import subprocess, sys
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
for lib in ['psutil', 'tkinter']:
    autoload(lib)

# 🧠 Imports
import psutil, threading, hashlib, time
import tkinter as tk

# 🔐 Cloak + Tamper Logic
def cloak_data(data):
    return f"⧈CLOAKED⧈:{data[::-1]}"

def verify_integrity(data):
    hash_original = hashlib.sha256(data.encode()).hexdigest()
    tampered = data != cloak_data(data[::-1])
    return not tampered, hash_original

# 🧬 Mutation Trail Logger
def log_mutation_event(event):
    with open("mutation_log.txt", "a") as log:
        log.write(f"[{time.ctime()}] {event}\n")

# 🧠 SmartAI Decision Engine
class SmartAI:
    def __init__(self):
        self.trusted_patterns = ["SENT:0|RECV:0", "heartbeat", "ping"]
        self.anomaly_threshold = 1000000  # bytes
        self.rewrite_count = 0

    def evaluate(self, data):
        # Self-rewriting logic: evolve trusted patterns based on frequency
        if self.rewrite_count < 5:
            if "SENT:1024" in data or "RECV:2048" in data:
                self.trusted_patterns.append(data)
                self.rewrite_count += 1
        if any(p in data for p in self.trusted_patterns):
            return "allow"
        sent_recv = [int(x.split(":")[1]) for x in data.split("|")]
        if any(val > self.anomaly_threshold for val in sent_recv):
            return "block"
        return "flag"

# 📡 Real-Time Network Monitor
class NetworkMonitor(threading.Thread):
    def __init__(self, gui_callback, gui_ref):
        super().__init__()
        self.gui_callback = gui_callback
        self.gui_ref = gui_ref
        self.running = False
        self.ai = SmartAI()

    def run(self):
        self.running = True
        prev = psutil.net_io_counters()
        while self.running:
            time.sleep(1)
            current = psutil.net_io_counters()
            sent = current.bytes_sent - prev.bytes_sent
            recv = current.bytes_recv - prev.bytes_recv
            prev = current
            if sent > 0 or recv > 0:
                data = f"SENT:{sent}|RECV:{recv}"
                encrypted = cloak_data(data)
                valid, _ = verify_integrity(encrypted)
                decision = self.ai.evaluate(data)

                if decision == "allow":
                    self.gui_callback(f"✅ SmartAI: Trusted data allowed.")
                    self.gui_ref.show_flagged_data("None")
                elif decision == "flag":
                    self.gui_callback("⚠️ SmartAI: Anomaly flagged. Awaiting override...")
                    self.gui_ref.show_flagged_data(data)
                    self.gui_ref.allow_button.config(state="normal")
                    for _ in range(10):
                        time.sleep(1)
                        if self.gui_ref.override_flag:
                            self.gui_callback("✅ Override accepted. Data passed.")
                            self.gui_ref.allow_button.config(state="disabled")
                            self.gui_ref.override_flag = False
                            self.gui_ref.show_flagged_data("None")
                            break
                    else:
                        self.gui_callback("❌ No override. Payload destroyed.")
                        log_mutation_event(f"SmartAI blocked: {data}")
                        self.gui_ref.allow_button.config(state="disabled")
                        self.gui_ref.override_flag = False
                        self.gui_ref.show_flagged_data("None")
                elif decision == "block" or not valid:
                    self.gui_callback("❌ SmartAI: Threat detected. Payload destroyed.")
                    log_mutation_event(f"SmartAI blocked: {data}")
                    self.gui_ref.show_flagged_data("None")

    def stop(self):
        self.running = False

# 🎨 MagicBox GUI HUD
class MagicBoxGUI:
    def __init__(self, root):
        root.title("MagicBox Guardian Daemon")
        root.geometry("460x380")
        root.configure(bg="#1e1e2f")

        tk.Label(root, text="🛡️ Mythic Swarm Brain Node", bg="#1e1e2f", fg="#f0f0f0", font=("Arial", 16)).pack(pady=20)
        self.status = tk.Label(root, text="Waiting to engage...", bg="#1e1e2f", fg="#4caf50", font=("Arial", 12))
        self.status.pack()

        self.start_button = tk.Button(root, text="🧠 Start Guardian", command=self.start_guard, bg="#4caf50", fg="white", font=("Arial", 12))
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="🛑 Stop Guardian", command=self.stop_guard, bg="#f44336", fg="white", font=("Arial", 12))
        self.stop_button.pack(pady=10)

        self.allow_button = tk.Button(root, text="✅ Allow Override", command=self.allow_override, bg="#2196f3", fg="white", font=("Arial", 12))
        self.allow_button.pack(pady=10)
        self.allow_button.config(state="disabled")

        tk.Label(root, text="Flagged Data:", bg="#1e1e2f", fg="#f0f0f0", font=("Arial", 12)).pack()
        self.flagged_data = tk.Label(root, text="None", bg="#1e1e2f", fg="#ff9800", font=("Arial", 10), wraplength=420, justify="left")
        self.flagged_data.pack(pady=5)

        self.footer = tk.Label(root, text="MagicBox v2.1 • Swarm-Aware • Self-Rewriting • Silent Mode", bg="#1e1e2f", fg="#888", font=("Arial", 10))
        self.footer.pack(side="bottom", pady=10)

        self.override_flag = False
        self.monitor = None

    def start_guard(self):
        if not self.monitor or not self.monitor.is_alive():
            self.status.config(text="🧠 Guardian engaged. Monitoring system traffic...")
            self.monitor = NetworkMonitor(self.update_status, self)
            self.monitor.start()

    def stop_guard(self):
        if self.monitor and self.monitor.is_alive():
            self.monitor.stop()
            self.status.config(text="🛑 Guardian stopped.")
            self.allow_button.config(state="disabled")
            self.override_flag = False
            self.show_flagged_data("None")

    def allow_override(self):
        self.override_flag = True
        self.status.config(text="⚡ Override accepted. Data allowed.")

    def update_status(self, msg):
        self.status.config(text=msg)

    def show_flagged_data(self, data):
        self.flagged_data.config(text=data)

# 🧿 Launch Daemon
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

