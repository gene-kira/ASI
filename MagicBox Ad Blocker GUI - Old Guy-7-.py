# MagicBox Ad Blocker - Full Tactical Shell
import subprocess, sys, os, json, time, datetime, threading

# 🧙 Auto-loader
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(package)

for lib in ["tkinter", "requests"]:
    autoload(lib)

import tkinter as tk
from tkinter import messagebox
import requests

REGISTRY_FILE = "magicbox_override.json"
SWARM_ENDPOINT = "https://your-swarm-node.net/sync"  # Replace with your actual endpoint

def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {"allow": [], "block": []}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)

def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4)

# 🔐 Port-Specific Firewall Enforcement
def block_ip_ports(ip, domain=None, ports=[80, 443], source="manual"):
    for port in ports:
        cmd = f"iptables -A OUTPUT -d {ip} -p tcp --dport {port} -j DROP"
        subprocess.call(cmd, shell=True)
        log_event(f"[⛒] BLOCKED {ip}:{port} ({domain}) from {source}")

# 🔁 Swarm Sync
def sync_with_swarm():
    try:
        registry = load_registry()
        response = requests.post(SWARM_ENDPOINT, json=registry)
        log_event("[🔁] Swarm sync complete.")
    except Exception as e:
        log_event(f"[!] Swarm sync failed: {e}")

# 📥 Blocklist Fetcher
BLOCKLIST_URLS = {
    "StevenBlack": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "EasyList": "https://easylist.to/easylist/easylist.txt",
    "AdGuard": "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"
}

def fetch_blocklist():
    domains = []
    for source, url in BLOCKLIST_URLS.items():
        try:
            response = requests.get(url, timeout=10)
            lines = response.text.splitlines()
            for line in lines:
                if "ads" in line or "track" in line or "doubleclick" in line:
                    parts = line.split()
                    for part in parts:
                        if "." in part and not part.startswith("#"):
                            clean = part.strip().replace("0.0.0.0", "").replace("127.0.0.1", "").strip()
                            if clean and not clean.startswith("#"):
                                domains.append((clean, source))
                                log_event(f"[📥] DOWNLOADED: {clean} from {source}")
        except Exception as e:
            log_event(f"[!] ERROR fetching {source}: {e}")
    return domains

def update_registry(domains):
    registry = load_registry()
    now = str(datetime.datetime.now())
    for domain, source in domains:
        if not any(d["domain"] == domain for d in registry["block"]):
            try:
                ip = subprocess.check_output(f"dig +short {domain}", shell=True).decode().strip().split("\n")[0]
                if ip:
                    registry["block"].append({
                        "domain": domain,
                        "ip": ip,
                        "ports": [80, 443],
                        "timestamp": now,
                        "symbol": "⛒",
                        "mutation": "auto-detected",
                        "source": source
                    })
                    block_ip_ports(ip, domain, [80, 443], source)
            except Exception as e:
                log_event(f"[!] ERROR resolving {domain}: {e}")
    save_registry(registry)
    sync_with_swarm()

def daemon_loop():
    while True:
        log_event("[🔍] SCANNING for ad servers...")
        domains = fetch_blocklist()
        update_registry(domains)
        log_event(f"[⛒] BLOCKLIST updated with {len(domains)} domains.")
        time.sleep(3600)

# 🧙 GUI Setup
def launch_gui():
    registry = load_registry()

    root = tk.Tk()
    root.title("MAGICBOX AD BLOCKER - TACTICAL SHELL")
    root.geometry("700x600")
    root.configure(bg="#0f0f0f")

    status_label = tk.Label(root, text="SYSTEM READY", fg="#00ff00", bg="#0f0f0f", font=("Courier", 14, "bold"))
    status_label.pack(pady=10)

    domain_entry = tk.Entry(root, font=("Courier", 12), width=40, bg="#1f1f1f", fg="#ffffff", insertbackground="#ffffff")
    domain_entry.pack(pady=10)
    domain_entry.insert(0, "Enter domain or IP")

    log_box = tk.Text(root, height=10, width=80, bg="#1f1f1f", fg="#00ff00", font=("Courier", 10))
    log_box.pack(pady=10)

    firewall_box = tk.Text(root, height=15, width=80, bg="#1f1f1f", fg="#ffcc00", font=("Courier", 10))
    firewall_box.pack(pady=10)

    def log_event(message):
        log_box.insert(tk.END, message + "\n")
        log_box.see(tk.END)

    def update_firewall_panel():
        registry = load_registry()
        firewall_box.delete(1.0, tk.END)
        for entry in registry["block"]:
            line = f"{entry['domain']} ({entry.get('ip', 'N/A')}) → Ports: {entry.get('ports', [80,443])} | Source: {entry.get('source','?')} | {entry['symbol']}"
            firewall_box.insert(tk.END, line + "\n")

    def block_domain():
        domain = domain_entry.get().strip()
        if domain:
            now = str(datetime.datetime.now())
            try:
                ip = subprocess.check_output(f"dig +short {domain}", shell=True).decode().strip().split("\n")[0]
                if ip:
                    registry["block"].append({
                        "domain": domain,
                        "ip": ip,
                        "ports": [80, 443],
                        "timestamp": now,
                        "symbol": "⛒",
                        "mutation": "manual",
                        "source": "GUI"
                    })
                    save_registry(registry)
                    block_ip_ports(ip, domain, [80, 443], "GUI")
                    status_label.config(text=f"[⛒] BLOCKED: {domain}", fg="#ff4444")
                    update_firewall_panel()
            except Exception as e:
                log_event(f"[!] ERROR resolving {domain}: {e}")
        else:
            messagebox.showwarning("Input Error", "Enter a valid domain or IP.")

    def allow_domain():
        domain = domain_entry.get().strip()
        if domain:
            registry["allow"].append({
                "domain": domain,
                "timestamp": str(datetime.datetime.now()),
                "symbol": "⚖️",
                "mutation": "manual",
                "source": "GUI"
            })
            save_registry(registry)
            status_label.config(text=f"[⚖️] ALLOWED: {domain}", fg="#44ff44")
            log_event(f"[⚖️] ALLOWED: {domain}")
        else:
            messagebox.showwarning("Input Error", "Enter a valid domain or IP.")

    btn_frame = tk.Frame(root, bg="#0f0f0f")
    btn_frame.pack(pady=10)

    block_btn = tk.Button(btn_frame, text="⛒ BLOCK", command=block_domain, font=("Courier", 12, "bold"), bg="#ff0000", fg="white", width=12)
    block_btn.grid(row=0, column=0, padx=10)

    allow_btn = tk.Button(btn_frame, text="⚖️ ALLOW", command=allow_domain, font=("Courier", 12, "bold"), bg="#00aa00", fg="white", width=12)
    allow_btn.grid(row=0, column=1, padx=10)

    globals()["log_event"] = log_event
    update_firewall_panel()
    root.mainloop()

# 🚀 Launch Everything
if __name__ == "__main__":
    threading.Thread(target=daemon_loop, daemon=True).start()
    launch_gui()

