import sys, subprocess, ctypes, socket, struct, threading, time, re, importlib
import tkinter as tk
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import psutil, win32gui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# --- Setup ---
for lib in ["matplotlib", "selenium", "psutil", "pywin32"]:
    try: importlib.import_module(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
if not ctypes.windll.shell32.IsUserAnAdmin(): sys.exit("Run as admin")

# --- Network ---
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def start_sniff():
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    sock.bind((get_ip(), 0))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    return sock

# --- Ad Detection ---
AD_DOMAINS = [b"doubleclick", b"googlesyndication", b"adnxs", b"ads", b"track", b"banner"]
def classify(proto, length, payload):
    p = payload.lower()
    if any(d in p for d in AD_DOMAINS): return "Ad", "black"
    if b"video" in p: return "Video", "green"
    if b"json" in p or b"text" in p: return "Data", "blue"
    return "Other", "orange"

# --- Browser ---
def get_youtube():
    urls = []
    def cb(hwnd, _): 
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            m = re.search(r"(https://www\.youtube\.com/watch\?v=[\w-]+)", t)
            if m: urls.append(m.group(1))
    win32gui.EnumWindows(cb, urls)
    return urls[0] if urls else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

opts = Options()
for arg in ["--disable-infobars", "--mute-audio", "--start-maximized", "--disable-notifications", "--disable-popup-blocking"]:
    opts.add_argument(arg)
driver = webdriver.Chrome(options=opts)
driver.get(get_youtube())

def is_ad():
    try: return "ad-showing" in driver.find_element("css selector", ".html5-video-player").get_attribute("class")
    except: return False

def inject_js():
    js = """document.querySelectorAll('[id*="ad"], [class*="ad"], iframe[src*="ads"]').forEach(e => e.remove());"""
    try: driver.execute_script(js)
    except: pass

# --- GUI ---
class CognitionLab:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Sovereign Cognition Shell")
        self.root.geometry("1200x700")
        self.feed = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=40)
        self.feed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filter = ttk.Combobox(root, values=["All", "blue", "green", "orange", "black"])
        self.filter.set("All")
        self.filter.pack()
        self.toggle_btn = tk.Button(root, text="Turn OFF Ad Blocker", command=self.toggle_block)
        self.toggle_btn.pack()
        self.chart = self.setup_chart()
        self.sock = None
        self.blocking = True
        self.entropy = []
        self.log = []
        self.mutations = 0
        threading.Thread(target=self.ad_loop, daemon=True).start()
        self.root.after(1000, self.update)

    def setup_chart(self):
        fig, ax = plt.subplots(figsize=(6, 4))
        line, = ax.plot([], [], color='magenta')
        ax.set_ylim(0, 3)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().pack(side=tk.RIGHT)
        return (line, ax, canvas)

    def toggle_block(self):
        self.blocking = not self.blocking
        state = "ON" if self.blocking else "OFF"
        self.toggle_btn.config(text=f"Turn {'OFF' if self.blocking else 'ON'} Ad Blocker")
        self.feed.insert(tk.END, f"🛡️ Ad Blocker is now {state}.\n")

    def ad_loop(self):
        while True:
            if self.blocking and is_ad():
                self.mutations += 1
                self.feed.insert(tk.END, f"[Mutation #{self.mutations}] Ad detected — refreshing.\n")
                driver.refresh()
                time.sleep(5)
            inject_js()
            time.sleep(2)

    def update(self):
        if not self.sock: self.sock = start_sniff()
        try: data = self.sock.recvfrom(65565)[0]
        except: return
        if len(data) < 20: return
        ip = struct.unpack('!BBHHHBBH4s4s', data[:20])
        proto = ip[6]
        src = socket.inet_ntoa(ip[8])
        dst = socket.inet_ntoa(ip[9])
        payload = data[20:100]
        label, color = classify(proto, len(data), payload)
        ent = len(data)/1500 + (1 - {6:0.9,17:0.7}.get(proto,0.3))
        self.entropy.append(ent)
        msg = f"{src} → {dst} | {label} | Entropy: {round(ent,2)}"
        if self.filter.get() == "All" or self.filter.get() == color:
            self.feed.insert(tk.END, msg + "\n")
            self.feed.see(tk.END)
        self.update_chart()
        self.root.after(1000, self.update)

    def update_chart(self):
        line, ax, canvas = self.chart
        line.set_data(range(len(self.entropy)), self.entropy)
        ax.set_xlim(max(0, len(self.entropy)-100), len(self.entropy))
        canvas.draw()

# --- Launch ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CognitionLab(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (driver.quit(), root.destroy()))
    root.mainloop()

