import socket, threading, tkinter as tk, json, time, os, subprocess, sys, math
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from selenium import webdriver

# 🧠 Constants
MEMORY, CLOAK = [], {"cloaked": {"success": 0}, "telemetry": {"success": 0}, "youtube": {"success": 0}}
TELEMETRY = [
    "luckyorange.com", "sentry.io", "bugsnag.com", "freshworks.com", "log.byeoversea.com",
    "xiaomi.com", "huawei.com", "apple.com", "pagead.js", "ads.with-blocking-page-feature"
]
NODE_ID, TARGET_IP, PORTS = "God@JunctionCity", "127.0.0.1", range(1, 256)
FIREWALL = "telemetry_firewall"

# 🧠 GUI Setup
root = tk.Tk(); root.title("Borg Shell")
frame = tk.Frame(root); frame.pack()
logbox = ScrolledText(root, width=100, height=10); logbox.pack()

# 📊 Mutation Dashboard
columns = ("Time", "Cloak", "Domain", "Port", "Payload")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
for col in columns: tree.heading(col, text=col, command=lambda c=col: sort_by(c, False)); tree.column(col, width=150)
tree.pack()

# 🔍 Filter Controls
filter_frame = tk.Frame(root); filter_frame.pack()
filters = {col: tk.StringVar() for col in columns}
for i, col in enumerate(columns):
    tk.Label(filter_frame, text=col).grid(row=0, column=i)
    tk.Entry(filter_frame, textvariable=filters[col], width=15).grid(row=1, column=i)
tk.Button(filter_frame, text="Apply Filter", command=lambda: apply_filter()).grid(row=1, column=len(columns))

def log(msg): logbox.insert(tk.END, msg + "\n"); logbox.see(tk.END)

def save(): json.dump(MEMORY, open("asi_memory.json", "w")); json.dump(CLOAK, open("cloak_memory.json", "w"))

def update_dashboard(entry):
    tree.insert("", "end", values=(
        entry["time"], entry["cloak"], entry["domain"], entry["port"], entry["payload"][:50]
    ))

def log_event(domain, port, payload, cloak="cloaked"):
    entry = {
        "time": time.strftime("%H:%M:%S"),
        "domain": domain,
        "port": port,
        "payload": payload,
        "cloak": cloak,
        "node": NODE_ID
    }
    MEMORY.append(entry)
    CLOAK[cloak]["success"] += 1; save()
    log(f"[{cloak}] {domain}:{port} → {payload}")
    update_dashboard(entry)

def detect(domain, port, payload):
    if "youtube.com" in domain:
        log_event(domain, port, payload, "youtube")
        return
    if any(t in domain for t in TELEMETRY):
        log_event(domain, port, payload, "telemetry")
        os.makedirs(FIREWALL, exist_ok=True)
        with open(os.path.join(FIREWALL, "blocked.txt"), "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} BLOCKED {domain}\n")

def entropy(data):
    if not data: return 0
    freq = {b: data.count(b) for b in set(data)}
    return -sum((f/len(data)) * math.log2(f/len(data)) for f in freq.values())

def scan_tcp():
    for p in PORTS:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex((TARGET_IP, p)) == 0:
                log(f"TCP {p} OPEN"); detect("unknown.local", p, "tcp-connect")

def scan_udp():
    for p in PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            try:
                s.sendto(b'\x00', (TARGET_IP, p))
                data, _ = s.recvfrom(1024)
                score = entropy(data)
                log(f"UDP {p} Entropy {score:.2f}")
                detect("unknown.local", p, data.decode(errors='ignore'))
            except: pass

def export_dns():
    os.makedirs(FIREWALL, exist_ok=True)
    with open(os.path.join(FIREWALL, "AcrylicHosts.txt"), "w") as f:
        for d in TELEMETRY: f.write(f"127.0.0.1 {d}\n")
    log("DNS cloak exported")

def inject_youtube():
    try:
        driver = webdriver.Chrome()
        driver.get("https://youtube.com")
        driver.execute_script("""(function(){
            const cloak = sel => document.querySelectorAll(sel).forEach(e => {
                e.style.opacity = "0"; e.style.pointerEvents = "none"; e.style.height = "0px";
                e.setAttribute("data-cloaked", "true");
            });
            const S = ["#masthead-ad", "#player-ads", "iframe[src*='ads']", "[id*='ad']", "[class*='ad']"];
            new MutationObserver(() => S.forEach(cloak)).observe(document.body, {childList:1,subtree:1});
            setInterval(() => S.forEach(cloak), 3000);
            console.log("🧠 YouTube cloak active");
        })();""")
        log("YouTube cloak injected")
    except Exception as e: log(f"Selenium failed: {e}")

def autonomous():
    threading.Thread(target=scan_tcp, daemon=True).start()
    threading.Thread(target=scan_udp, daemon=True).start()
    threading.Thread(target=inject_youtube, daemon=True).start()
    export_dns()

# 🔍 Sorting
def sort_by(col, descending):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    data.sort(reverse=descending)
    for index, (_, k) in enumerate(data): tree.move(k, "", index)
    tree.heading(col, command=lambda: sort_by(col, not descending))

# 🔍 Filtering
def apply_filter():
    for i in tree.get_children(): tree.delete(i)
    for entry in MEMORY:
        if all(filters[col].get().lower() in str(entry[col]).lower() for col in columns if filters[col].get()):
            update_dashboard(entry)

tk.Button(frame, text="Autonomous Start", command=autonomous).pack()
log("🧠 Borg Shell Initialized"); log(f"🧿 Node: {NODE_ID}")
root.mainloop()
