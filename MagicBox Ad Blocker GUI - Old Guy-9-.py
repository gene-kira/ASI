import subprocess, sys, os, json, time, datetime, threading, math
import tkinter as tk
import requests

REGISTRY = "magicbox_override.json"
SWARM = "https://your-swarm-node.net/vote"  # Replace with your actual endpoint
PORTS = [80, 443]

def entropy(domain):
    c = {x: domain.count(x) for x in set(domain)}
    t = sum(c.values())
    return round(-sum((v/t)*math.log2(v/t) for v in c.values()), 2)

def load(): return json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {"allow": [], "block": []}
def save(data): json.dump(data, open(REGISTRY, "w"), indent=2)

def log(msg): LOG.insert(tk.END, msg + "\n"); LOG.see(tk.END)

def block(ip, domain, src, score):
    for p in PORTS:
        subprocess.call(f"iptables -A OUTPUT -d {ip} -p tcp --dport {p} -j DROP", shell=True)
        log(f"[⛒] BLOCKED {ip}:{p} ({domain}) from {src} | Entropy: {score}")

def vote(domain, symbol, score):
    try: requests.post(SWARM, json={"domain": domain, "symbol": symbol, "entropy": score})
    except: log(f"[!] Swarm vote failed for {domain}")

def fetch():
    urls = {
        "StevenBlack": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
        "EasyList": "https://easylist.to/easylist/easylist.txt",
        "AdGuard": "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"
    }
    found = []
    for src, url in urls.items():
        try:
            for line in requests.get(url, timeout=10).text.splitlines():
                if any(x in line for x in ["ads", "track", "doubleclick"]):
                    for part in line.split():
                        if "." in part and not part.startswith("#"):
                            d = part.replace("0.0.0.0", "").replace("127.0.0.1", "").strip()
                            if d: found.append((d, src)); log(f"[📥] {d} from {src}")
        except: log(f"[!] Error fetching {src}")
    return found

def update(domains):
    reg, now = load(), str(datetime.datetime.now())
    for d, src in domains:
        if not any(x["domain"] == d for x in reg["block"]):
            try:
                ip = subprocess.check_output(f"dig +short {d}", shell=True).decode().strip().split("\n")[0]
                score = entropy(d)
                reg["block"].append({"domain": d, "ip": ip, "ports": PORTS, "timestamp": now, "symbol": "⛒", "mutation": "auto", "source": src, "entropy": score})
                block(ip, d, src, score)
                if score > 4.5: log(f"[⚛️] Quantum burst: {d} ({score})")
                vote(d, "⛒", score)
            except: log(f"[!] Resolve failed: {d}")
    save(reg)

def daemon(): 
    while True: log("[🔍] Scanning..."); update(fetch()); log("[⛒] Blocklist updated."); time.sleep(3600)

def gui():
    reg = load()
    root = tk.Tk(); root.title("MAGICBOX - QUANTUM SWARM"); root.geometry("800x650"); root.configure(bg="#0f0f0f")
    status = tk.Label(root, text="READY", fg="#00ff00", bg="#0f0f0f", font=("Courier", 14, "bold")); status.pack(pady=10)
    entry = tk.Entry(root, font=("Courier", 12), width=40, bg="#1f1f1f", fg="#fff", insertbackground="#fff"); entry.pack(pady=10); entry.insert(0, "Enter domain or IP")
    global LOG; LOG = tk.Text(root, height=10, width=90, bg="#1f1f1f", fg="#0f0", font=("Courier", 10)); LOG.pack(pady=10)
    FW = tk.Text(root, height=15, width=90, bg="#1f1f1f", fg="#fc0", font=("Courier", 10)); FW.pack(pady=10)

    def refresh():
        FW.delete(1.0, tk.END)
        for x in load()["block"]:
            FW.insert(tk.END, f"{x['domain']} ({x['ip']}) → Ports: {x['ports']} | Source: {x['source']} | Entropy: {x['entropy']} | {x['symbol']}\n")

    def block_manual():
        d, now = entry.get().strip(), str(datetime.datetime.now())
        if d:
            try:
                ip = subprocess.check_output(f"dig +short {d}", shell=True).decode().strip().split("\n")[0]
                score = entropy(d)
                reg["block"].append({"domain": d, "ip": ip, "ports": PORTS, "timestamp": now, "symbol": "⛒", "mutation": "manual", "source": "GUI", "entropy": score})
                save(reg); block(ip, d, "GUI", score); vote(d, "⛒", score)
                status.config(text=f"[⛒] BLOCKED: {d}", fg="#f44"); refresh()
            except: log(f"[!] Resolve failed: {d}")

    def allow_manual():
        d = entry.get().strip()
        if d:
            reg["allow"].append({"domain": d, "timestamp": str(datetime.datetime.now()), "symbol": "⚖️", "mutation": "manual", "source": "GUI"})
            save(reg); status.config(text=f"[⚖️] ALLOWED: {d}", fg="#4f4"); log(f"[⚖️] ALLOWED: {d}")

    frame = tk.Frame(root, bg="#0f0f0f"); frame.pack(pady=10)
    tk.Button(frame, text="⛒ BLOCK", command=block_manual, font=("Courier", 12, "bold"), bg="#f00", fg="white", width=12).grid(row=0, column=0, padx=10)
    tk.Button(frame, text="⚖️ ALLOW", command=allow_manual, font=("Courier", 12, "bold"), bg="#0a0", fg="white", width=12).grid(row=0, column=1, padx=10)
    refresh(); root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=daemon, daemon=True).start()
    gui()

