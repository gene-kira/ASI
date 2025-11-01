# Codex DNS Sentinel – Real-Time DNS Logger with Persistent Folder Memory
import os, sys, time, socket, threading, platform, json

CONFIG_FILE = os.path.expanduser("~\\CodexDNS\\dns_config.json")

# 🔺 Elevation Check (Windows only)
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

if not is_admin():
    if platform.system() == "Windows":
        import ctypes
        script_path = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script_path, None, 1)
        sys.exit()

# 🖥️ GUI Overlay
try:
    import tkinter as tk
    from tkinter import ttk, filedialog
except ImportError:
    os.system(f"{sys.executable} -m pip install tk")
    import tkinter as tk
    from tkinter import ttk, filedialog

# 📁 Persistent Folder Selection
def get_saved_folder():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                folder = data.get("log_folder")
                if folder and os.path.exists(folder):
                    return folder
        except Exception:
            pass
    return None

def save_folder(folder):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"log_folder": folder}, f)

def select_log_folder():
    saved = get_saved_folder()
    if saved:
        return saved
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder for DNS Logs")
    if not folder:
        sys.exit("No folder selected. Exiting.")
    save_folder(folder)
    return folder

log_folder = select_log_folder()
os.makedirs(log_folder, exist_ok=True)
LOG_PATH = os.path.join(log_folder, "dns_queries.log")
RESURRECTED_PATH = os.path.join(log_folder, "resurrected_domains.log")

# 🧿 Resurrection Detection
resolved_domains = set()
def detect_resurrection(domain):
    if domain in resolved_domains:
        with open(RESURRECTED_PATH, "a") as f:
            f.write(f"{time.ctime()} | RESURRECTED: {domain}\n")
        return True
    resolved_domains.add(domain)
    return False

# 📜 DNS Query Logger
def log_dns_query(domain, ip):
    with open(LOG_PATH, "a") as f:
        f.write(f"{time.ctime()} | {domain} -> {ip}\n")

class DNSOverlay:
    def __init__(self, root, log_location):
        self.root = root
        self.root.title("Codex DNS Sentinel")
        self.root.geometry("650x350")
        self.root.configure(bg="#1e1e1e")

        self.label = tk.Label(root, text=f"Logs saved to: {log_location}", fg="lime", bg="#1e1e1e", font=("Segoe UI", 10, "bold"))
        self.label.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("Domain", "IP", "Resurrected"), show="headings")
        self.tree.heading("Domain", text="Domain")
        self.tree.heading("IP", text="Resolved IP")
        self.tree.heading("Resurrected", text="Resurrected")
        self.tree.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", rowheight=25)
        style.map("Treeview", background=[("selected", "#333333")])

    def update(self, domain, ip, resurrected):
        self.tree.insert("", "end", values=(domain, ip, "🧿" if resurrected else ""))

gui_instance = None
def update_gui(domain, ip, resurrected):
    if gui_instance:
        gui_instance.update(domain, ip, resurrected)

# 🌐 Real-Time DNS Resolution Monitor
def monitor_dns():
    import psutil
    seen = set()
    while True:
        conns = psutil.net_connections(kind='inet')
        for conn in conns:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                ip = conn.raddr.ip
                try:
                    domain = socket.gethostbyaddr(ip)[0]
                    if domain not in seen:
                        seen.add(domain)
                        resurrected = detect_resurrection(domain)
                        log_dns_query(domain, ip)
                        update_gui(domain, ip, resurrected)
                except Exception:
                    continue
        time.sleep(5)

# 🔥 Ignite
if __name__ == "__main__":
    root = tk.Tk()
    gui_instance = DNSOverlay(root, log_folder)
    threading.Thread(target=monitor_dns, daemon=True).start()
    root.mainloop()

