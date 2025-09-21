import sys
import subprocess
import importlib
import logging
import ctypes
import socket
import struct
from collections import deque
import tkinter as tk
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# 🧠 Autoloader Daemon
def autoload(libraries):
    for lib in libraries:
        try:
            importlib.import_module(lib)
            logging.info(f"✅ {lib} loaded.")
        except ImportError:
            logging.info(f"🔧 Installing {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            logging.info(f"✅ Installed {lib}")

required_libraries = ["matplotlib"]
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
autoload(required_libraries)

# 🔐 Admin Privilege Check
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("❌ Administrator privileges required. Please run as admin.")
    sys.exit(1)

# 🌐 Auto-Detect Host IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 🧬 Chromatic Cognition Engine
def classify_flow(proto_id, pkt_len, payload):
    payload_lower = payload.lower()
    is_video = b"video" in payload_lower or b"mp4" in payload_lower or b"stream" in payload_lower
    is_data = b"json" in payload_lower or b"text" in payload_lower or b"xml" in payload_lower
    is_hostile = b"malware" in payload_lower or pkt_len > 2000

    if is_hostile:
        return "Hostile", "red"
    elif is_video and is_data:
        return "Data+Video", "purple"
    elif is_video:
        return "Video", "green"
    elif is_data:
        return "Data", "blue"
    else:
        return "Drifting", "orange"

# 🔍 Packet Dissection
packet_log = []
entropy_stream = deque(maxlen=100)

def dissect_packet(data):
    if len(data) < 20:
        return
    ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
    proto_id = ip_header[6]
    src_ip = socket.inet_ntoa(ip_header[8])
    dst_ip = socket.inet_ntoa(ip_header[9])
    pkt_len = len(data)
    payload = data[20:100]
    status, color = classify_flow(proto_id, pkt_len, payload)
    proto_name = {6: "TCP", 17: "UDP"}.get(proto_id, "Other")
    entropy = pkt_len / 1500 + (1 - {6: 0.9, 17: 0.7}.get(proto_id, 0.3))
    entropy_stream.append(entropy)
    story = f"{proto_name} flow from {src_ip} to {dst_ip} | Type: {status} | Entropy: {round(entropy,2)}"
    packet_log.append((story, color))

def start_capture():
    try:
        host_ip = get_local_ip()
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sock.bind((host_ip, 0))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        return sock
    except Exception as e:
        packet_log.append((f"Socket error: {e}", "red"))
        return None

# 🖥️ GUI Shell
class AnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧪 Sovereign Cognition Lab")
        self.root.geometry("1200x700")

        # Left Panel
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.feed = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=60, height=40)
        self.feed.pack(pady=10)

        control_frame = tk.Frame(left_frame)
        control_frame.pack()

        self.color_filter = ttk.Combobox(control_frame, values=["All", "blue", "green", "purple", "orange", "red"])
        self.color_filter.set("All")
        self.color_filter.pack(side=tk.LEFT)

        override_btn = tk.Button(control_frame, text="🗳️ Override Ritual", command=self.override_ritual)
        override_btn.pack(side=tk.LEFT, padx=10)

        start_btn = tk.Button(left_frame, text="🔬 Start Dissection", command=self.start_sniffing)
        start_btn.pack(pady=10)

        # Right Panel: Pulse Chart
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.line, = self.ax.plot([], [], color='magenta')
        self.ax.set_ylim(0, 3)
        self.ax.set_xlim(0, 100)
        self.ax.set_title("Glyph Pulse Monitor")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack()

        self.capture_socket = None
        self.root.after(1000, self.update_loop)

    def start_sniffing(self):
        self.feed.insert(tk.END, "🔍 Continuous cognition initiated...\n")
        self.capture_socket = start_capture()

    def update_loop(self):
        if self.capture_socket:
            try:
                data = self.capture_socket.recvfrom(65565)[0]
                dissect_packet(data)
            except Exception as e:
                packet_log.append((f"Socket error: {e}", "red"))
        if packet_log:
            story, color = packet_log.pop(0)
            if self.color_filter.get() == "All" or self.color_filter.get() == color:
                self.feed.insert(tk.END, story + "\n")
                self.feed.see(tk.END)
        self.update_chart()
        self.root.after(1000, self.update_loop)

    def update_chart(self):
        self.line.set_data(range(len(entropy_stream)), list(entropy_stream))
        self.ax.set_xlim(max(0, len(entropy_stream)-100), len(entropy_stream))
        self.canvas.draw()

    def override_ritual(self):
        self.feed.insert(tk.END, "🗳️ Executive override ritual triggered.\n")

# 🧠 Launch
if __name__ == "__main__":
    root = tk.Tk()
    gui = AnalyzerGUI(root)
    root.mainloop()
