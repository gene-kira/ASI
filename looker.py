import subprocess
import sys

# 🧬 Autoloader for required libraries
def autoload_libraries():
    required = ['requests']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

import socket
import struct
import requests
import tkinter as tk
from datetime import datetime

# 🌐 Auto-detect local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# 🌍 Country code → full name map
country_map = {
    "US": "United States", "DE": "Germany", "FR": "France", "CN": "China", "RU": "Russia",
    "IN": "India", "BR": "Brazil", "JP": "Japan", "GB": "United Kingdom", "CA": "Canada"
    # Add more as needed
}

# 🌍 Resolve IP to country name and org
def get_country_info(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        data = r.json()
        code = data.get("country", "Unknown")
        org = data.get("org", "Unknown")
        return country_map.get(code, code), org
    except:
        return "Unknown", "Unknown"

# 🧙 GUI Shell with symbolic overlays
class IPMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 Sovereign IP Monitor Shell")
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg="black")
        self.canvas.pack()
        self.glyphs = {}
        self.y_offset = 20

    def add_glyph(self, ip, country, org):
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"{timestamp} → {ip} → {country} → {org}"
        glyph = self.canvas.create_text(10, self.y_offset, anchor="nw", text=text, fill="lime", font=("Consolas", 12))
        self.glyphs[ip] = glyph
        self.y_offset += 20
        self.root.update()

    def run(self):
        self.root.mainloop()

# 🧪 Raw socket sniffer
def sniff(gui):
    local_ip = get_local_ip()
    print(f"[+] Binding to local IP: {local_ip}")
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.bind((local_ip, 0))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    seen_ips = set()

    while True:
        packet = s.recvfrom(65565)[0]
        ip_header = packet[0:20]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
        src_ip = socket.inet_ntoa(iph[8])

        if src_ip not in seen_ips and src_ip != local_ip:
            seen_ips.add(src_ip)
            country, org = get_country_info(src_ip)
            print(f"[+] New IP: {src_ip} from {country} ({org})")
            gui.add_glyph(src_ip, country, org)

# 🚀 Launch shell
if __name__ == "__main__":
    gui = IPMonitorGUI()
    import threading
    t = threading.Thread(target=sniff, args=(gui,), daemon=True)
    t.start()
    gui.run()
