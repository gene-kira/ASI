import tkinter as tk, math, numpy as np, sounddevice as sd, pyttsx3, zmq, json, threading, time, hashlib, psutil, os
from random import uniform
try: import cupy as cp; GPU = True
except: GPU = False
try: import GPUtil
except: GPU = False

# --- Codex ---
CODEX_PATH = "codex.json"
DEFAULT_CODEX = {
    "retention": 300,
    "purge": 60,
    "ghost": {"enabled": True, "drift": 10},
    "threats": []
}
def load_codex():
    if not os.path.exists(CODEX_PATH):
        with open(CODEX_PATH, "w") as f: json.dump(DEFAULT_CODEX, f)
    with open(CODEX_PATH, "r") as f: return json.load(f)
def save_codex(c): json.dump(c, open(CODEX_PATH, "w"))
def ghost_sync(m, c): return abs(time.time() - m.get("timestamp", 0)) > c.get("ghost", {}).get("drift", 10)
def rewrite(c):
    c["retention"] = max(60, int(c.get("retention", 300)) // 2)
    c.setdefault("threats", []).append("phantom_node")
    save_codex(c)
def codex_hash(c): return hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
def sync_codex(pub, c): pub.send_string(json.dumps({"codex_sync": {"codex": c, "hash": codex_hash(c)}}))
def receive_codex(msg, c):
    p = msg.get("codex_sync"); return p["codex"] if p and codex_hash(p["codex"]) == p["hash"] else c

# --- Forces ---
def forces(m1, m2, r, q1=1e-6, q2=1e-6):
    G, k = 6.67430e-11, 8.9875517923e9
    return G*m1*m2/r**2, k*q1*q2/r**2, 1e2/r**2 if r < 1e-15 else 0, 1e-3/r**2 if r < 1e-18 else 0
def drift_dilation(t, base=1e8):
    drift = base + math.sin(t / 2) * base * 0.5
    dilation = 1 / math.sqrt(1 - drift**2 / (3e8)**2)
    return drift, dilation
def compute(m1, m2, r, v):
    g, e, s, w = forces(m1, m2, r)
    drift, dilation = drift_dilation(time.time())
    base = g + e + s + w
    velocity_factor = 1 + v**2 / (3e8)**2
    F = base * velocity_factor * dilation
    return F, "GPU" if GPU else "CPU", drift, dilation, (g, e, s, w)

# --- Feedback ---
engine = pyttsx3.init()
voice_enabled = True
volume_level = 0.5
def tone(F):
    t = np.linspace(0, 0.5, int(44100 * 0.5), False)
    freq = 200 + F / 1e10
    pitch = 440 + F / 1e11
    wave = (np.sin(freq * t * 2 * np.pi) + np.sin(pitch * t * 2 * np.pi)) * volume_level
    sd.play(wave, 44100); sd.wait()
def narrate(F, mode, telemetry, dilation, forces):
    if not voice_enabled: return
    g, e, s, w = forces
    phrase = f"Force {F:.2e} N. Mode {mode}. Dilation {dilation:.2f}. G:{g:.2e} EM:{e:.2e} S:{s:.2e} W:{w:.2e}. CPU:{telemetry['cpu']} RAM:{telemetry['ram']} GPU:{telemetry['gpu']}"
    engine.say(phrase); engine.runAndWait()

# --- Swarm Sync ---
ctx = zmq.Context(); pub = ctx.socket(zmq.PUB); pub.bind("tcp://*:5555")
sub = ctx.socket(zmq.SUB); sub.connect("tcp://localhost:5555"); sub.setsockopt_string(zmq.SUBSCRIBE, "")
def sonic_hash(m): return hashlib.sha256(f"{m['F']}{m['timestamp']}".encode()).hexdigest()
def broadcast(F): pub.send_string(json.dumps({"F": F, "timestamp": time.time(), "hash": sonic_hash({"F": F, "timestamp": time.time()})}))
def listen():
    global codex
    while True:
        try:
            msg = json.loads(sub.recv_string())
            if "codex_sync" in msg: codex = receive_codex(msg, codex); continue
            if ghost_sync(msg, codex): rewrite(codex)
            if msg.get("hash") == sonic_hash(msg): tone(msg["F"])
        except: pass
threading.Thread(target=listen, daemon=True).start()

# --- Telemetry ---
def telemetry():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "gpu": round(GPUtil.getGPUs()[0].load * 100) if GPU else 0
    }

# --- GUI ---
def overlay(F, dilation):
    if dilation < 1.05:
        canvas.config(bg="lightblue"); glyph.config(text="⊕"); polarity.config(text="Stable 🧊")
    elif dilation < 1.2:
        canvas.config(bg="violet"); glyph.config(text="∞"); polarity.config(text="Shifting ⚡")
    else:
        canvas.config(bg="red"); glyph.config(text="Ψ"); polarity.config(text="Critical 🔥")
    result.config(text=f"F' = {F:.2e} N")
def update(F, mode, telemetry, dilation):
    mode_label.config(text=f"Mode: {mode}")
    stats.config(text=f"CPU:{telemetry['cpu']} RAM:{telemetry['ram']} GPU:{telemetry['gpu']}")
    overlay(F, dilation)
def toggle_voice():
    global voice_enabled
    voice_enabled = not voice_enabled
    voice_button.config(text=f"Voice: {'ON 🗣️' if voice_enabled else 'OFF 🔇'}")
def update_volume(val):
    global volume_level
    volume_level = float(val)

# --- Autonomous Loop ---
def loop():
    t = time.time()
    while True:
        m1, m2 = 5 + math.cos(t / 5) * 2, 10 + math.sin(t / 7) * 3
        r, v = uniform(1, 10), abs(math.sin(t / 3)) * 2.5e8
        F, mode, drift, dilation, Fx = compute(m1, m2, r, v)
        T = telemetry(); update(F, mode, T, dilation)
        tone(F); narrate(F, mode, T, dilation, Fx)
        broadcast(F); sync_codex(pub, codex)
        t += 2; time.sleep(2)

# --- GUI Setup ---
root = tk.Tk(); root.title("🧠 Quantum Cognition Mesh")
canvas = tk.Canvas(root, width=300, height=50); canvas.pack()
polarity = tk.Label(root); polarity.pack()
glyph = tk.Label(root); glyph.pack()
mode_label = tk.Label(root); mode_label.pack()
stats = tk.Label(root); stats.pack()
result = tk.Label(root); result.pack()
voice_button = tk.Button(root, text="Voice: ON 🗣️", command=toggle_voice); voice_button.pack()
tk.Label(root, text="🔊 Volume").pack()
volume_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.01,
                         orient=tk.HORIZONTAL, command=update_volume)
volume_slider.set(volume_level); volume_slider.pack()

# --- Launch ---
codex = load_codex()
threading.Thread(target=loop, daemon=True).start()
root.mainloop()

