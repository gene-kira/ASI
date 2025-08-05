import sys
import subprocess
import importlib
import platform
import psutil
import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import networkx as nx
import pyttsx3

# 🔄 Auto-install required packages
required_libs = ['networkx', 'matplotlib', 'tkinter', 'psutil', 'pyttsx3']
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🎙 Voice Narration Module
class VoiceReactor:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.enabled = True

    def speak(self, message):
        if self.enabled:
            self.engine.say(message)
            self.engine.runAndWait()

    def toggle_voice(self):
        self.enabled = not self.enabled
        return self.enabled

# 🧠 ASI Tracker
class ASILogger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(f"[ASI-Log] {message}")

    def get_logs(self):
        return '\n'.join(self.logs)

# 🧩 Core Hopper with Override Logic
class MagicBoxHopper:
    def __init__(self, asi, voice):
        self.G = nx.Graph()
        self.asi = asi
        self.voice = voice

    def load_graph(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    src, dst, weight = line.strip().split(',')
                    self.G.add_edge(src, dst, weight=int(weight))
            self.asi.log(f"Loaded graph from {path}")
        except Exception as e:
            self.asi.log(f"Graph load failed: {e}")

    def shortest_hop(self, start, end):
        try:
            path = nx.shortest_path(self.G, source=start, target=end, weight='weight')
            self.asi.log(f"Shortest path {start} → {end}: {path}")
            return path
        except Exception as e:
            self.asi.log(f"Hop error: {e}")
            return []

    def trace_hop_count(self, ip):
        cmd = ['tracert', '-d', ip] if platform.system() == 'Windows' else ['traceroute', ip]
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.splitlines()
        hops = len([line for line in lines if line.strip() and line.strip()[0].isdigit()])
        return hops

    def reroute_ip(self, ip):
        try:
            cmd = (['route', 'ADD', ip, 'MASK', '255.255.255.255', '192.168.1.1']
                   if platform.system() == 'Windows'
                   else ['ip', 'route', 'add', ip, 'via', '192.168.1.1'])
            subprocess.run(cmd, check=True)
            self.asi.log(f"Override route for {ip} → 192.168.1.1")
            self.voice.speak(f"Overmind override: rerouted {ip}")
        except Exception as e:
            self.asi.log(f"Route change failed for {ip}: {e}")
            self.voice.speak(f"Failed to override route for {ip}")

    def scan_outbound_system_data(self):
        connections = psutil.net_connections(kind='inet')
        outbound = [c for c in connections if c.status == 'ESTABLISHED' and c.raddr]
        result = {}

        for conn in outbound:
            ip = conn.raddr.ip
            hops = self.trace_hop_count(ip)
            mood = ''
            if hops < 5:
                mood = 'green'
                self.voice.speak(f"{ip} is optimal. Overmind pleased.")
            elif hops <= 10:
                mood = 'orange'
                self.voice.speak(f"{ip} is borderline. Overmind uncertain.")
            else:
                mood = 'red'
                self.reroute_ip(ip)
                self.voice.speak(f"{ip} is dangerous. Rerouting engaged.")
            self.asi.log(f"{ip} → {hops} hops [{mood}]")
            result[ip] = f"{hops} hops [{mood}]"
        return result

# 🎛 GUI Interface
class MagicBoxGUI:
    def __init__(self, hopper, voice):
        self.hopper = hopper
        self.voice = voice
        self.root = tk.Tk()
        self.root.title("MagicBox Hopper 🌌 Overmind Theater Edition")
        self.root.geometry("500x400")
        self.root.configure(bg="#1c1f2a")

        self.build_interface()

    def build_interface(self):
        tk.Label(self.root, text="Start Node:", bg="#1c1f2a", fg="white").pack()
        self.start_entry = tk.Entry(self.root)
        self.start_entry.pack()

        tk.Label(self.root, text="End Node:", bg="#1c1f2a", fg="white").pack()
        self.end_entry = tk.Entry(self.root)
        self.end_entry.pack()

        tk.Button(self.root, text="Load Graph File", command=self.load_graph).pack(pady=5)
        tk.Button(self.root, text="Find Shortest Hop", command=self.find_shortest_hop).pack(pady=5)
        tk.Button(self.root, text="Scan & Optimize Hops 🚀", command=self.scan_and_optimize).pack(pady=5)
        tk.Button(self.root, text="Show ASI Logs 📜", command=self.show_logs).pack(pady=5)
        self.voice_button = tk.Button(self.root, text="Voice OFF 🔇", command=self.toggle_voice)
        self.voice_button.pack(pady=5)

    def load_graph(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.hopper.load_graph(path)

    def find_shortest_hop(self):
        start = self.start_entry.get()
        end = self.end_entry.get()
        path = self.hopper.shortest_hop(start, end)
        messagebox.showinfo("Shortest Hop", f"{path}")

    def scan_and_optimize(self):
        results = self.hopper.scan_outbound_system_data()
        display = "\n".join([f"{ip}: {info}" for ip, info in results.items()])
        messagebox.showinfo("Hop Scan Results", display or "No outbound data found.")

    def show_logs(self):
        logs = self.hopper.asi.get_logs()
        messagebox.showinfo("ASI Logs", logs)

    def toggle_voice(self):
        enabled = self.voice.toggle_voice()
        self.voice_button.config(text="Voice ON 🔊" if not enabled else "Voice OFF 🔇")

    def run(self):
        self.root.mainloop()

# 🚀 Launch the program
if __name__ == '__main__':
    asi_logger = ASILogger()
    voice = VoiceReactor()
    hopper = MagicBoxHopper(asi_logger, voice)
    gui = MagicBoxGUI(hopper, voice)
    gui.run()

