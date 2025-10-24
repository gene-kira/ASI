import sys, time, json, socket, sqlite3, threading, ctypes
from tkinter import Tk, Canvas, ttk, Entry, Button
from concurrent.futures import ThreadPoolExecutor
import numpy as np, sounddevice as sd, serial, psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def ensure_admin():
    try: is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except: is_admin = False
    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(f'"{a}"' for a in sys.argv), None, 1)
        sys.exit()

DB, log, codex = "asi.db", [], {"DTMF_911": "purge", "PING_ACK": "retain"}
last_audio = 0

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS reg (
            sym TEXT PRIMARY KEY, src TEXT, threat TEXT, country TEXT,
            purge TEXT, synced INT, port TEXT, dir TEXT)''')

def set_reg(sym, meta):
    with sqlite3.connect(DB) as c:
        c.execute('''INSERT OR REPLACE INTO reg VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (sym, meta["src"], meta["threat"], meta["country"], codex.get(sym, "retain"),
                   0, meta["port"], meta["dir"]))

def get_reg():
    with sqlite3.connect(DB) as c:
        return {r[0]: dict(zip(["src", "threat", "country", "purge", "synced", "port", "dir"], r[1:]))
                for r in c.execute("SELECT * FROM reg")}

def fuse(sym, meta):
    if len(get_reg()) > 1000: return
    set_reg(sym, meta)
    log.append(f"{time.strftime('%H:%M:%S')} | {sym} via {meta['port']}")
    log[:] = log[-500:]

def mutate(reg):
    for k, v in reg.items():
        if list(reg).count(k) > 3 and v["threat"] == "high" and codex.get(k) != "purge":
            codex[k] = "purge"
            log.append(f"{time.strftime('%H:%M:%S')} | Codex mutated: {k} → purge")

def sync(reg):
    with sqlite3.connect(DB) as c:
        for k in reg:
            c.execute("UPDATE reg SET synced=1 WHERE sym=?", (k,))
            log.append(f"{time.strftime('%H:%M:%S')} | Synced {k}")

def cluster(reg):
    C = {}
    for k, v in reg.items():
        key = f"{v['threat']}_{v['country']}_{v['port']}_{v['dir']}"
        C.setdefault(key, []).append((k, v))
    return C

def decode(signal, sr=44100, th=0.3):
    unit = int(sr * 0.1)
    bits = ''.join(['1' if abs(s) > th else '0' for s in signal])
    i, out = 0, []
    while i < len(bits):
        if bits[i] == '1':
            l = bits[i:].find('0')
            out.append('.' if l < unit else '-')
            i += l if l > 0 else 1
        else:
            i += 1
    return ''.join(out)

def audio_cb(indata, *_):
    global last_audio
    if time.time() - last_audio < 0.5:
        return
    last_audio = time.time()
    try:
        data = indata[:, 0]
        fft = np.abs(np.fft.fft(data))
        f = np.fft.fftfreq(len(data), d=1/44100)
        anomaly = np.max(fft[(f > 1000) & (f < 1200)]) > 0.3
        sym = decode(data)
        if sym:
            fuse(sym, {
                "src": "audio",
                "threat": "high" if anomaly else "low",
                "country": "unknown",
                "port": "MIC",
                "dir": "input"
            })
    except Exception as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Audio error: {e}")

def net():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        while True:
            try:
                d, a = s.recvfrom(1024)
                sym = d.decode(errors='ignore')
                if sym:
                    fuse(sym, {
                        "src": "net",
                        "threat": "medium",
                        "country": "US" if a[0].startswith("192.") else "Unknown",
                        "port": f"UDP:{port}",
                        "dir": "input"
                    })
            except Exception as e:
                log.append(f"{time.strftime('%H:%M:%S')} | Net recv error: {e}")
    except Exception as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Network init error: {e}")

def serial_in():
    try:
        s = serial.Serial('COM3', 9600)
        while True:
            try:
                line = s.readline().decode(errors='ignore').strip()
                if line:
                    fuse(line, {
                        "src": "serial",
                        "threat": "low",
                        "country": "US",
                        "port": "COM3",
                        "dir": "input"
                    })
            except Exception as e:
                log.append(f"{time.strftime('%H:%M:%S')} | Serial read error: {e}")
    except Exception as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Serial init error: {e}")

class Watch(FileSystemEventHandler):
    def on_created(self, e):
        log.append(f"{time.strftime('%H:%M:%S')} | File created: {e.src_path}")
    def on_modified(self, e):
        log.append(f"{time.strftime('%H:%M:%S')} | File modified: {e.src_path}")
    def on_deleted(self, e):
        log.append(f"{time.strftime('%H:%M:%S')} | File deleted: {e.src_path}")

def monitor():
    try:
        o = Observer()
        o.schedule(Watch(), "C:\\Users\\Public", recursive=True)
        o.start()
    except Exception as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Monitor error: {e}")

def gui():
    root = Tk()
    root.title("ASI Console")
    root.geometry("1200x800")
    root.configure(bg="#0f0f0f")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#0f0f0f", foreground="#00ffff", font=("Consolas", 10))
    style.configure("Header.TLabel", foreground="#ff00ff", font=("Consolas", 12, "bold"))
    nb, tabs, panels = ttk.Notebook(root), {}, {}
    nb.pack(fill="both", expand=True)

    for name in ["Live", "Registry", "Threats", "Swarm", "Codex", "Hardware", "Events"]:
        f = ttk.Frame(nb)
        nb.add(f, text=name)
        ttk.Label(f, text=name, style="Header.TLabel").pack(anchor="w")
        l = ttk.Label(f, text="Awaiting input...", wraplength=1000, justify="left")
        l.pack(anchor="w")
        tabs[name], panels[name] = f, l

    canvas = Canvas(tabs["Swarm"], width=1000, height=400, bg="#1a1a1a")
    canvas.pack()
    s_entry, r_entry = Entry(tabs["Codex"]), Entry(tabs["Codex"])
    ttk.Label(tabs["Codex"], text="Symbol:").pack(anchor="w")
    s_entry.pack(anchor="w")
    ttk.Label(tabs["Codex"], text="Rule:").pack(anchor="w")
    r_entry.pack(anchor="w")
    Button(tabs["Codex"], text="Apply", command=lambda: codex.update({s_entry.get(): r_entry.get()})).pack(anchor="w")

    def update():
        try:
            reg = get_reg()
            sync(reg)
            mutate(reg)
            cl = cluster(reg)
            panels["Live"].config(text=f"Decoded: {next(iter(reg), 'None')}")
            panels["Registry"].config(text="\n".join([f"{k}: {v}" for k, v in list(reg.items())[:50]]))
            panels["Threats"].config(text="High: {}\nMedium: {}\nLow: {}".format(
                sum(v["threat"] == "high" for v in reg.values()),
                sum(v["threat"] == "medium" for v in reg.values()),
                sum(v["threat"] == "low" for v in reg.values())))
            canvas.delete("all")
            y = 50
            for c, syms in list(cl.items())[:5]:
                color = "#00ff00" if "low" in c else "#ffaa00" if "medium" in c else "#ff0033"
                canvas.create_text(50, y - 20, text=f"Cluster: {c}", fill="#ffffff", font=("Consolas", 10))
                for i, (s, meta) in enumerate(syms[:4]):
                    x = 50 + (i % 4) * 120
                    pulse = "#00ffff" if meta.get("synced") else "#444444"
                    canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color, outline=pulse, width=2)
                    safe_sym = str(s) if s else "?"
                    overlay = f"{safe_sym[:10]}\n{meta.get('port', '?')}/{meta.get('dir', '?')}\n{meta.get('threat', '?')}"
                    canvas.create_text(x, y + 30, text=overlay, fill="#ffffff", font=("Consolas", 7))
                y += 100
            panels["Codex"].config(text="\n".join([f"{k}: {v}" for k, v in codex.items()]))
            panels["Hardware"].config(text=f"Drives: {[p.device for p in psutil.disk_partitions() if 'rw' in p.opts]}\nWebcam: No unauthorized access detected")
            panels["Events"].config(text="\n".join(log[-20:]) or "No events yet.")
        except Exception as e:
            log.append(f"{time.strftime('%H:%M:%S')} | GUI update error: {e}")
        root.after(1000, update)

    update()
    return root

# === Launch ===
if __name__ == "__main__":
    ensure_admin()
    init_db()
    try:
        sd.InputStream(
            callback=audio_cb,
            channels=1,
            samplerate=44100,
            blocksize=2048,
            latency='high',
            exception_on_overflow=False,
            finished_callback=lambda: log.append(f"{time.strftime('%H:%M:%S')} | Audio stream finished")
        ).start()
    except Exception as e:
        log.append(f"{time.strftime('%H:%M:%S')} | Audio stream error: {e}")
    pool = ThreadPoolExecutor(max_workers=4)
    pool.submit(net)
    pool.submit(serial_in)
    pool.submit(monitor)
    gui().mainloop()

