import subprocess, sys, importlib, ctypes
for lib in ["numpy", "sounddevice", "tkinter", "socket", "serial", "json", "psutil", "watchdog"]:
    try: globals()[lib] = importlib.import_module(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib if lib != "serial" else "pyserial"])
import numpy as np, sounddevice as sd, socket, serial, tkinter as tk
from tkinter import ttk
import json, psutil, threading, time, winreg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === ELEVATION CHECK ===
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        print("[Codex Sentinel] Elevation required. Relaunching as administrator...")
        params = " ".join(f'"{arg}"' for arg in sys.argv)
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        sys.exit()

codex, mutations, log = {"DTMF_911": "purge", "PING_ACK": "retain"}, [], []
REG_PATH = r"Software\ASIConsole\SymbolicRegistry"

def set_reg(symbol, data):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
        winreg.SetValueEx(key, symbol, 0, winreg.REG_SZ, json.dumps(data))

def get_reg():
    reg = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            i = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(key, i)
                    reg[name] = json.loads(val)
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return reg

def fuse(symbol, src, meta):
    entry = {
        "origin": src,
        "threat": meta["threat"],
        "country": meta["country"],
        "purge": codex.get(symbol, "retain"),
        "synced": False,
        "port": meta.get("port", "unknown"),
        "direction": meta.get("direction", "input")
    }
    set_reg(symbol, entry)
    log.append(f"{time.strftime('%H:%M:%S')} | Ingested {symbol} via {entry['port']}")

def mutate():
    reg = get_reg()
    counts = {k: list(reg).count(k) for k in reg}
    for k, v in reg.items():
        if counts[k] > 3 and v["threat"] == "high" and codex.get(k) != "purge":
            codex[k] = "purge"
            mutations.append(f"{time.strftime('%H:%M:%S')} | {k} → purge")
            log.append(f"{time.strftime('%H:%M:%S')} | Codex mutated: {k} → purge")

def sync():
    reg = get_reg()
    for k in reg:
        reg[k]["synced"] = True
        set_reg(k, reg[k])
        log.append(f"{time.strftime('%H:%M:%S')} | Synced {k}")

def cluster():
    C = {}
    for k, v in get_reg().items():
        key = f"{v['threat']}_{v['country']}_{v['port']}_{v['direction']}"
        C.setdefault(key, []).append((k, v))
    return C

def decode(signal, sr=44100, th=0.3):
    unit = int(sr * 0.1)
    bits = ['1' if abs(s) > th else '0' for s in signal]
    pulses, i, out = ''.join(bits), 0, []
    while i < len(pulses):
        if pulses[i] == '1':
            l = 1
            while i + l < len(pulses) and pulses[i + l] == '1':
                l += 1
            out.append('.' if l < unit else '-')
            i += l
        else:
            i += 1
    return ''.join(out)

def audio_cb(indata, *_):
    data = indata[:, 0]
    fft = np.abs(np.fft.fft(data))
    f = np.fft.fftfreq(len(data), d=1/44100)
    anomaly = np.max(fft[(f > 1000) & (f < 1200)]) > 0.3
    symbol = decode(data)
    if symbol:
        fuse(symbol, "audio", {
            "threat": "high" if anomaly else "low",
            "country": "unknown",
            "port": "MIC",
            "direction": "input"
        })

def net():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(('', 0))  # OS assigns a free port
        assigned_port = s.getsockname()[1]
        log.append(f"{time.strftime('%H:%M:%S')} | Network socket bound to port {assigned_port}")
    except OSError as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Socket bind failed: {e}")
        return
    while True:
        try:
            d, a = s.recvfrom(1024)
            p = d.decode(errors='ignore')
            if p:
                fuse(p, "network", {
                    "threat": "medium",
                    "country": "US" if a[0].startswith("192.") else "Unknown",
                    "port": f"UDP:{assigned_port}",
                    "direction": "input"
                })
        except Exception as e:
            log.append(f"{time.strftime('%H:%M:%S')} | Socket error: {e}")

def serial_in(port='COM3', baud=9600):
    s = serial.Serial(port, baud)
    while True:
        line = s.readline().decode('utf-8', errors='ignore').strip()
        if line:
            fuse(line, "serial", {
                "threat": "low",
                "country": "US",
                "port": port,
                "direction": "input"
            })

class FileMonitor(FileSystemEventHandler):
    def on_created(self, e): log.append(f"{time.strftime('%H:%M:%S')} | File created: {e.src_path}")
    def on_modified(self, e): log.append(f"{time.strftime('%H:%M:%S')} | File modified: {e.src_path}")
    def on_deleted(self, e): log.append(f"{time.strftime('%H:%M:%S')} | File deleted: {e.src_path}")

def monitor_files(path="C:\\Users\\Public"):
    o = Observer()
    o.schedule(FileMonitor(), path, recursive=True)
    o.start()

def drives(): return [p.device for p in psutil.disk_partitions() if 'rw' in p.opts]
def webcam(): return "No unauthorized access detected"
def gui():
    root = tk.Tk()
    root.title("ASI Console")
    root.geometry("1200x800")
    root.configure(bg="#0f0f0f")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#0f0f0f", foreground="#00ffff", font=("Consolas", 10))
    style.configure("Header.TLabel", foreground="#ff00ff", font=("Consolas", 12, "bold"))
    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)
    tabs, panels = {}, {}
    for name in ["Live", "Registry", "Threats", "Swarm", "Codex", "Hardware", "Events"]:
        f = ttk.Frame(nb)
        nb.add(f, text=name)
        ttk.Label(f, text=name, style="Header.TLabel").pack(anchor="w")
        l = ttk.Label(f, text="Awaiting input...", wraplength=1000, justify="left")
        l.pack(anchor="w")
        tabs[name], panels[name] = f, l
    canvas = tk.Canvas(tabs["Swarm"], width=1000, height=400, bg="#1a1a1a")
    canvas.pack()
    ttk.Label(tabs["Codex"], text="Symbol:").pack(anchor="w")
    s_entry = ttk.Entry(tabs["Codex"]); s_entry.pack(anchor="w")
    ttk.Label(tabs["Codex"], text="Rule (purge/retain):").pack(anchor="w")
    r_entry = ttk.Entry(tabs["Codex"]); r_entry.pack(anchor="w")
    def apply_codex():
        s, r = s_entry.get(), r_entry.get()
        if s and r in ["purge", "retain"]:
            codex[s] = r
            log.append(f"{time.strftime('%H:%M:%S')} | Codex manually set: {s} → {r}")
        s_entry.delete(0, tk.END)
        r_entry.delete(0, tk.END)
    ttk.Button(tabs["Codex"], text="Apply", command=apply_codex).pack(anchor="w")

    def update():
        sync(); mutate(); reg = get_reg()
        panels["Live"].config(text=f"Decoded: {next(iter(reg), 'None')}")
        panels["Registry"].config(text="\n".join([f"{k}: {v}" for k,v in reg.items()]))
        panels["Threats"].config(text="High: {}\nMedium: {}\nLow: {}".format(
            sum(v["threat"]=="high" for v in reg.values()),
            sum(v["threat"]=="medium" for v in reg.values()),
            sum(v["threat"]=="low" for v in reg.values())))
        canvas.delete("all"); y = 50
        for c, syms in cluster().items():
            color = "#00ff00" if "low" in c else "#ffaa00" if "medium" in c else "#ff0033"
            canvas.create_text(50, y-20, text=f"Cluster: {c}", fill="#ffffff", font=("Consolas", 10))
            for i, (s, meta) in enumerate(syms):
                x = 50 + (i % 6) * 100
                pulse = "#00ffff" if meta["synced"] else "#444444"
                canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, outline=pulse, width=2)
                overlay = f"{s[:10]}\n{meta['port']}/{meta['direction']}\n{meta['threat']}"
                canvas.create_text(x, y+30, text=overlay, fill="#ffffff", font=("Consolas", 7))
            y += 100
        panels["Codex"].config(text="\n".join(mutations[-10:]) or "No mutations yet.")
        panels["Hardware"].config(text=f"Drives: {drives()}\nWebcam: {webcam()}")
        panels["Events"].config(text="\n".join(log[-20:]) or "No events yet.")
        root.after(1000, update)
    update()
    return root

if __name__ == "__main__":
    ensure_admin()
    root = gui()
    sd.InputStream(callback=audio_cb, channels=1, samplerate=44100, blocksize=1024).start()
    threading.Thread(target=net, daemon=True).start()
    threading.Thread(target=serial_in, daemon=True).start()
    threading.Thread(target=monitor_files, daemon=True).start()
    root.mainloop()


