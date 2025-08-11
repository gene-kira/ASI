# 🔧 Auto-loader for required libraries
import subprocess
import sys

def autoload_libraries():
    required = ["wmi", "psutil", "py-cpuinfo", "tkinterdnd2", "gputil"]
    for lib in required:
        try:
            __import__(lib.replace("py-", "").replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

# 🧠 Imports after autoload
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from threading import Thread
import time
import wmi
import psutil
import cpuinfo
import GPUtil
import subprocess

# 🧙‍♂️ MagicBox GUI Class
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧿 MagicBox Sentinel")
        self.root.geometry("600x800")
        self.root.configure(bg="#1e1e2f")

        self.title = tk.Label(root, text="🧙‍♂️ MagicBox Sentinel HUD", font=("Helvetica", 18, "bold"), fg="#00ffe0", bg="#1e1e2f")
        self.title.pack(pady=15)

        self.voltage_frame = tk.Frame(root, bg="#1e1e2f")
        self.voltage_frame.pack()

        self.gpu_frame = tk.Frame(root, bg="#1e1e2f")
        self.gpu_frame.pack(pady=10)

        self.labels = {}
        self.gpu_labels = {}

        self.status = tk.Label(root, text="Initializing...", fg="#8888aa", bg="#1e1e2f", font=("Helvetica", 12))
        self.status.pack(pady=10)

        self.identity_btn = tk.Button(root, text="🧠 Show System Identity", command=self.display_identity, font=("Helvetica", 14), bg="#444466", fg="white")
        self.identity_btn.pack(pady=5)

        self.asi_btn = tk.Button(root, text="🛡️ Run ASI Scan", command=self.run_asi_scan, font=("Helvetica", 14), bg="#664444", fg="white")
        self.asi_btn.pack(pady=5)

        self.drop_zone = tk.Label(root, text="📂 Drop files here", font=("Helvetica", 14), bg="#333355", fg="#ffffff", width=40, height=4)
        self.drop_zone.pack(pady=10)
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)

        self.node_canvas = tk.Canvas(root, width=580, height=200, bg="#1e1e2f", highlightthickness=0)
        self.node_canvas.pack()
        self.nodes = []

        self.update_thread = Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    # ⚡ Voltage Reader with Fallback
    def get_voltage_info(self):
        try:
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            return {s.Name: s.Value for s in sensors if s.SensorType == 'Voltage'}
        except Exception:
            return {
                "CPU Usage": psutil.cpu_percent(interval=1),
                "CPU Temp": "Unavailable",
                "Fallback": True
            }

    # 🎮 GPU Info with Fallback
    def get_gpu_info(self):
        try:
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            gpu_data = {}
            for s in sensors:
                if "GPU" in s.Name and s.SensorType in ['Temperature', 'Load', 'Fan']:
                    gpu_data[s.Name] = f"{s.Value:.1f} {s.SensorType}"
            if gpu_data:
                return gpu_data
        except:
            pass

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "GPU Name": gpu.name,
                    "GPU Load": f"{gpu.load*100:.1f}%",
                    "GPU Temp": f"{gpu.temperature} °C",
                    "GPU Memory": f"{gpu.memoryUsed}/{gpu.memoryTotal} MB"
                }
        except:
            return {"GPU": "Unavailable"}

        return {"GPU": "No data"}

    # 🔄 Real-Time Update Loop
    def update_loop(self):
        while True:
            volts = self.get_voltage_info()
            self.status.config(text="🧠 Scanning...")

            for name, value in volts.items():
                if name not in self.labels:
                    lbl = tk.Label(self.voltage_frame, text=f"{name}: {value}", font=("Helvetica", 12), fg="#ffaa00", bg="#1e1e2f")
                    lbl.pack()
                    self.labels[name] = lbl
                else:
                    self.labels[name].config(text=f"{name}: {value}")

            if volts.get("Fallback"):
                self.status.config(text="⚠️ OpenHardwareMonitor not found—using fallback")

            gpu_info = self.get_gpu_info()
            for name, value in gpu_info.items():
                if name not in self.gpu_labels:
                    lbl = tk.Label(self.gpu_frame, text=f"{name}: {value}", font=("Helvetica", 12), fg="#00aaff", bg="#1e1e2f")
                    lbl.pack()
                    self.gpu_labels[name] = lbl
                else:
                    self.gpu_labels[name].config(text=f"{name}: {value}")

            time.sleep(2)

    # 🧬 System Identity Display
    def display_identity(self):
        info = cpuinfo.get_cpu_info()
        cpu_model = info.get("brand_raw", "Unknown")
        arch = info.get("arch", "Unknown")
        vendor = info.get("vendor_id_raw", "Unknown")

        try:
            output = subprocess.run(["wmic", "bios", "get", "smbiosbiosversion"], capture_output=True, text=True)
            bios_version = output.stdout.split("\n")[1].strip()
        except:
            bios_version = "Unknown"

        try:
            output2 = subprocess.run(["wmic", "computersystem", "get", "manufacturer,model"], capture_output=True, text=True)
            lines = output2.stdout.split("\n")[1:]
            system_info = [line.strip() for line in lines if line.strip()]
        except:
            system_info = ["Unknown"]

        identity_window = tk.Toplevel(self.root)
        identity_window.title("🧠 System Identity")
        identity_window.configure(bg="#2f2f3f")

        tk.Label(identity_window, text=f"CPU: {cpu_model}", font=("Helvetica", 12), bg="#2f2f3f", fg="#00ffff").pack()
        tk.Label(identity_window, text=f"Arch: {arch} | Vendor: {vendor}", font=("Helvetica", 12), bg="#2f2f3f", fg="#00ffff").pack()
        tk.Label(identity_window, text=f"BIOS: {bios_version}", font=("Helvetica", 12), bg="#2f2f3f", fg="#ffaa00").pack()
        for s in system_info:
            tk.Label(identity_window, text=s, font=("Helvetica", 12), bg="#2f2f3f", fg="#ffffff").pack()

    # 🛡️ ASI Threat Scan
    def run_asi_scan(self):
        ports = [conn.laddr.port for conn in psutil.net_connections() if conn.status == 'LISTEN']
        asi_window = tk.Toplevel(self.root)
        asi_window.title("🛡️ ASI Threat Scan")
        asi_window.configure(bg="#3f2f2f")

        for port in ports:
            if port == 3389:
                msg = "⚠️ RDP port open—high risk"
                color = "#ff4444"
            elif port == 22:
                msg = "⚠️ SSH port open—medium risk"
                color = "#ffaa00"
            else:
                msg = f"Port {port} open—unknown risk"
                color = "#cccccc"

            tk.Label(asi_window, text=msg, font=("Helvetica", 12), bg="#3f2f2f", fg=color).pack()

        if not ports:
            tk.Label(asi_window, text="✅ No suspicious ports found", font=("Helvetica", 12), bg="#3f2f2f", fg="#00ff88").pack()

    # 📂 Handle Real File Drop
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for f in files:
            self.create_node(f.split("/")[-1])

    # 🌀 Node Creation with Symbolic Overlay
    def create_node(self, name):
        x = 50 + len(self.nodes)*100
        y = 100
        node = self.node_canvas.create_oval(x, y, x+40, y+40, fill="#00ffaa", outline="#ffffff")
        label = self.node

    # 🌀 Node Creation with Symbolic Overlay
    def create_node(self, name):
        x = 50 + len(self.nodes)*100
        y = 100
        node = self.node_canvas.create_oval(x, y, x+40, y+40, fill="#00ffaa", outline="#ffffff")
        label = self.node_canvas.create_text(x+20, y+20, text="🌀", font=("Helvetica", 14))
        aura = self.node_canvas.create_oval(x-10, y-10, x+50, y+50, outline="#ff00ff", width=2)
        self.nodes.append((node, label, aura))

# 🚀 Launch the GUI
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

