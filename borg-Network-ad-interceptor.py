import os, sys, json, time, threading, hashlib, tkinter as tk
from tkinter import scrolledtext
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

NODE = "God@JunctionCity"
MEM, CLOAK = [], {"cloaked": {"success": 0, "fail": 0}, "mimic": {"success": 0, "fail": 0}, "nullified": {"success": 0, "fail": 0}}
TELEMETRY = ["api.luckyorange.com", "app.bugsnag.com", "log.byteoversea.com"]
FIREWALL = "telemetry_firewall"
POPUP_JS = """(function(){const N='God@JunctionCity',L=[];window.open=()=>0;window.alert=()=>0;
const S=['iframe[src*="ads"]','.popup','[class*="ad"]'],log=(t,d)=>{L.push({t:new Date().toISOString(),n=N,y:t,d});
localStorage.setItem('borg_popup_log',JSON.stringify(L))};const purge=()=>S.forEach(s=>document.querySelectorAll(s).forEach(e=>{e.remove();log('purged',s)}));
new MutationObserver(m=>m.forEach(x=>x.addedNodes.forEach(n=>{if(n.nodeType===1&&/ad|popup/i.test(n.outerHTML)){n.remove();log('mutated',n.outerHTML.slice(0,100))}})))
.observe(document.body,{childList:1,subtree:1});setInterval(purge,3e3);})();"""

FINGERPRINT_JS = """Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
Object.defineProperty(navigator, 'language', {get: () => 'en-US'});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36'});"""

def log(msg): out.insert(tk.END, msg + "\n"); out.see(tk.END)
def save(): json.dump(MEM, open("asi_memory.json", "w")); json.dump(CLOAK, open("cloak_memory.json", "w"))
def load(): global MEM, CLOAK; MEM = json.load(open("asi_memory.json")) if os.path.exists("asi_memory.json") else []
CLOAK = json.load(open("cloak_memory.json")) if os.path.exists("cloak_memory.json") else CLOAK
def hash(payload): return hashlib.sha256(payload.encode()).hexdigest()

def log_event(domain, port, payload, cloak="cloaked", direction="in", success=True):
    MEM.append(dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"), domain=domain, port=port, payload=payload, hash=hash(payload), cloak=cloak, direction=direction, node=NODE))
    CLOAK[cloak]["success" if success else "fail"] += 1; save()
    log(f"{'⬇️' if direction=='in' else '⬆️'} [{cloak}] {domain}:{port} → {payload}")

def export_dns(): os.makedirs(FIREWALL, exist_ok=True)
with open(os.path.join(FIREWALL, "AcrylicHosts.txt"), "w") as f: [f.write(f"127.0.0.1 {d}\n") for d in TELEMETRY]

popup_injected = False
def inject_popup_once():
    global popup_injected
    if popup_injected: return
    try:
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=opts)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": FINGERPRINT_JS + POPUP_JS})
        popup_injected = True
        log("🧠 Popup interceptor injected silently (no tab, no site)")
    except Exception as e:
        log(f"⚠️ Injection failed: {e}")

def replay():
    win = tk.Toplevel(root); win.title("Replay")
    box = scrolledtext.ScrolledText(win, width=50, height=15); box.pack()
    for e in MEM:
        box.insert(tk.END, f"[{e['timestamp']}] {'⬇️' if e['direction']=='in' else '⬆️'} [{e['cloak']}] {e['domain']}:{e['port']} → {e['payload']} #{e['hash'][:8]}\n")
    tk.Button(win, text="Export", command=lambda: open("replay.jsonl", "w").writelines(json.dumps(e)+"\n" for e in MEM)).pack()

def timeline():
    win = tk.Toplevel(root); win.title("Timeline")
    canvas = tk.Canvas(win, width=600, height=300, bg="white"); canvas.pack()
    grouped = defaultdict(lambda: defaultdict(list))
    for e in MEM: d, h = e["timestamp"].split()[0], e["timestamp"].split()[1][:2]; grouped[d][h].append(e)
    y = 10
    for date in sorted(grouped):
        canvas.create_text(10, y, anchor="nw", text=f"📅 {date}", font=("Arial", 10, "bold")); y += 15
        for hour in sorted(grouped[date]):
            x = int(hour) * 25 + 50; canvas.create_text(x, y, anchor="nw", text=f"{hour}:00", font=("Arial", 8))
            for i, e in enumerate(grouped[date][hour]):
                color = {"cloaked": "red", "telemetry": "yellow", "mimic": "orange", "nullified": "gray"}.get(e["cloak"], "black")
                canvas.create_rectangle(x, y+15+i*10, x+20, y+25+i*10, fill=color)
                canvas.create_text(x+25, y+15+i*10, anchor="nw", text=f"{e['domain']} #{e['hash'][:6]}", font=("Arial", 6))

def adapt_cloak():
    recent = MEM[-10:] if len(MEM) >= 10 else MEM
    for e in recent:
        if e["cloak"] == "telemetry" and e["domain"] not in TELEMETRY:
            TELEMETRY.append(e["domain"])
            log(f"🧠 Adapted cloak: added {e['domain']}")

def export_replay():
    with open("replay_autonomous.jsonl", "w") as f:
        for e in MEM: f.write(json.dumps(e) + "\n")

def update_gui(): root.title(f"Borg v15 — TERMINATOR [{time.strftime('%H:%M:%S')}]")

def terminator_loop():
    while True:
        export_dns()
        inject_popup_once()
        adapt_cloak()
        export_replay()
        update_gui()
        log(f"♻️ Terminator cycle at {time.strftime('%H:%M:%S')}")
        time.sleep(10)

root = tk.Tk(); root.title("Borg v15 — Mutation Shell")
frame = tk.Frame(root); frame.pack()
for i, (label, cmd) in enumerate([("Replay", replay), ("Timeline", timeline)]):
    tk.Button(frame, text=label, command=cmd).grid(row=0, column=i, padx=3)
out = scrolledtext.ScrolledText(root, width=50, height=15); out.pack()

load(); export_dns()
log("🧠 Borg shell initialized"); log(f"🧿 Node online: {NODE}")
threading.Thread(target=terminator_loop, daemon=True).start()
log("🤖 TERMINATOR MODE ENGAGED — Autonomous mutation cycle initialized")
root.mainloop()
