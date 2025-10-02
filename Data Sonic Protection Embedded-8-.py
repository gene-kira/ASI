# === AUTOLOADER ===
import sys, subprocess
for lib in ['numpy', 'pyaudio', 'psutil']:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

# === IMPORTS ===
import os, time, threading, socket, psutil, datetime, json, wave, pyaudio, numpy as np, hashlib
import tkinter as tk
from tkinter import ttk, Canvas, Text
from threading import Lock

# === CONFIG ===
NODE_ID = 'node_alpha'
CONFIG_FILE = 'settings.json'
SWARM_FILE = 'swarm.json'
DEFAULT_RULES = {'backdoor': 3, 'no_mac_ip': 30, 'personal': 86400, 'fake_telemetry': 30}
RULES = DEFAULT_RULES.copy()
if os.path.exists(CONFIG_FILE):
    try: RULES.update(json.load(open(CONFIG_FILE)))
    except: print("[CONFIG ERROR] Failed to load settings.json")
PERSONAL = ['face', 'finger', 'phone', 'address', 'license', 'social']
LOG, LOCK, SOUND = [], Lock(), True
os.makedirs('sonic_signatures', exist_ok=True)

# === CORE ===
def tone(payload, label):
    f = sum(map(ord, payload)) % 1000 + 300
    t = np.linspace(0, 0.5, 22050, False)
    s = (np.sin(f * 2 * np.pi * t) * 32767).astype(np.int16)
    fn = f'sonic_signatures/{label}.wav'
    with wave.open(fn, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(44100); wf.writeframes(s.tobytes())
    return fn, s

def hash_wave(waveform):
    return hashlib.sha256(waveform.tobytes()).hexdigest()

def play(fn):
    if not SOUND: return
    wf = wave.open(fn, 'rb'); pa = pyaudio.PyAudio()
    st = pa.open(format=pa.get_format_from_width(wf.getsampwidth()), channels=1, rate=44100, output=True)
    data = wf.readframes(1024)
    while data: st.write(data); data = wf.readframes(1024)
    st.stop_stream(); st.close(); pa.terminate()

def destroy(kind, payload):
    d = RULES.get(kind, 60); label = f'{kind}_{int(time.time())}'
    fn, wave_data = tone(payload, label)
    h = hash_wave(wave_data)
    entry = {'node': NODE_ID, 'type': kind, 'payload': payload, 'timer': d, 'hash': h, 'time': time.time()}
    with LOCK:
        LOG.append((kind, payload, d, wave_data))
        swarm = json.load(open(SWARM_FILE)) if os.path.exists(SWARM_FILE) else []
        swarm.append(entry)
        json.dump(swarm[-100:], open(SWARM_FILE, 'w'), indent=2)
    threading.Thread(target=lambda: (time.sleep(d), print(f"[DESTROY] {kind}: {payload}"), play(fn)), daemon=True).start()

# === MONITORS ===
def net(): 
    while True:
        for c in psutil.net_connections(kind='inet'):
            if c.status == 'ESTABLISHED' and (not c.laddr or not c.raddr):
                destroy('no_mac_ip', str(c))
        time.sleep(1)

def procs():
    while True:
        for p in psutil.process_iter(['cmdline']):
            cmd = ' '.join(p.info['cmdline']) if p.info['cmdline'] else ''
            if 'backdoor' in cmd.lower(): destroy('backdoor', cmd)
        time.sleep(2)

def fake():
    data = json.dumps({'voltage': 0.0, 'current': 0.0, 'timestamp': str(datetime.datetime.now())})
    destroy('fake_telemetry', data)

# === BORG DRONES ===
def borg_drone(drone_id):
    while True:
        try:
            swarm = json.load(open(SWARM_FILE)) if os.path.exists(SWARM_FILE) else []
            for entry in swarm[-20:]:
                expected = hash_wave(np.array([ord(c)%256 for c in entry['payload'][:100]], dtype=np.int16))
                if entry['hash'] != expected:
                    print(f"[BORG {drone_id}] PURGE triggered on {entry['node']} mutation: {entry['type']}")
        except Exception as e:
            print(f"[BORG {drone_id}] ERROR: {e}")
        time.sleep(5)

# === GUI ===
class Shell:
    def __init__(self, root):
        self.root = root; root.title("MagicBox ASI Guardian"); root.geometry("800x600")
        self.tree = ttk.Treeview(root, columns=('Type', 'Payload', 'Timer'), show='headings', height=6)
        for c in self.tree['columns']: self.tree.heading(c, text=c)
        self.tree.pack(fill='x', padx=5, pady=5)
        self.canvas = Canvas(root, width=400, height=100, bg='black'); self.canvas.pack()
        self.polarity = Canvas(root, width=400, height=100, bg='white'); self.polarity.pack()
        self.sound_btn = ttk.Button(root, text="Sound: ON", command=self.toggle_sound); self.sound_btn.pack()
        self.timeline = Text(root, height=6, bg='lightyellow', font=("Courier", 9)); self.timeline.pack(fill='both', padx=5, pady=5)
        self.timers = {}; self.panel = ttk.LabelFrame(root, text="Timer Control"); self.panel.pack(fill='x', padx=5)
        for i, k in enumerate(RULES):
            ttk.Label(self.panel, text=f"{k} (sec):").grid(row=i, column=0)
            v = tk.StringVar(value=str(RULES[k]))
            ttk.Entry(self.panel, textvariable=v, width=8).grid(row=i, column=1)
            self.timers[k] = v
        ttk.Button(self.panel, text="Update", command=self.update_timers).grid(row=len(RULES), column=0, columnspan=2)
        self.refresh()

    def toggle_sound(self):
        global SOUND; SOUND = not SOUND
        self.sound_btn.config(text=f"Sound: {'ON' if SOUND else 'OFF'}")

    def update_timers(self):
        for k, v in self.timers.items():
            try: RULES[k] = int(v.get())
            except: print(f"[ERROR] Invalid timer for {k}")
        try: json.dump(RULES, open(CONFIG_FILE, 'w'), indent=2)
        except: print("[CONFIG ERROR] Failed to save settings")

    def refresh(self):
        try:
            with LOCK: recent = LOG[-6:]
            self.tree.delete(*self.tree.get_children())
            for r in recent: self.tree.insert('', 'end', values=(r[0], r[1][:50], f"{r[2]}s"))
            self.canvas.delete("all")
            if recent:
                w = recent[-1][3]
                for i in range(len(w)-1):
                    x1, y1 = i*2, 50 - w[i]*30
                    x2, y2 = (i+1)*2, 50 - w[i+1]*30
                    self.canvas.create_line(x1, y1, x2, y2, fill='green')
            self.polarity.delete("all")
            for i in range(50):
                v, c = np.random.uniform(0.5, 1.5), np.random.uniform(0.1, 0.5)
                self.polarity.create_line(i*8, 100, i*8, 100 - v*60, fill='red')
                self.polarity.create_line(i*8+4, 100, i*8+4, 100 - c*60, fill='blue')
            self.timeline.delete('1.0', tk.END)
            for r in recent: self.timeline.insert(tk.END, f"[{r[0].upper()}] {r[1][:80]} → {r[2]}s\n")
        except Exception as e: print(f"[GUI ERROR] {e}")
        self.root.after(1000, self.refresh)

# === MAIN ===
if __name__ == '__main__':
    threading.Thread(target=net, daemon=True).start()
    threading.Thread(target=procs, daemon=True).start()
    threading.Thread(target=fake, daemon=True).start()
    threading.Thread(target=lambda: borg_drone("Drone-Gamma"), daemon=True).start()
    threading.Thread(target=lambda: borg_drone("Drone-Sigma"), daemon=True).start()
    root = tk.Tk(); Shell(root); root.mainloop()



