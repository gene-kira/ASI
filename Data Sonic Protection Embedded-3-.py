# === AUTOLOADER ===
import sys, subprocess
required = ['numpy', 'pyaudio', 'psutil']
for lib in required:
    try:
        __import__(lib)
    except ImportError:
        print(f"[AUTOLOADER] Installing missing library: {lib}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

# === MAIN SHELL ===
import os, time, threading, socket, psutil, datetime, json
import numpy as np
import wave, pyaudio
import tkinter as tk
from tkinter import ttk, Canvas, Text
from threading import Lock

# === CONFIGURATION ===
PERSONAL_KEYS = ['face', 'finger', 'phone', 'address', 'license', 'social']
DESTRUCT_RULES = {
    'backdoor': 3,
    'no_mac_ip': 30,
    'personal': 86400,
    'fake_telemetry': 30
}
SONIC_DIR = 'sonic_signatures'
os.makedirs(SONIC_DIR, exist_ok=True)
sound_enabled = True
mutation_log = []
mutation_lock = Lock()

# === SONIC SIGNATURE GENERATION ===
def generate_sonic_signature(payload, label):
    tone_freq = sum(ord(c) for c in payload) % 1000 + 300
    duration = 0.5
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(tone_freq * 2 * np.pi * t)
    audio = (tone * 32767).astype(np.int16)
    filename = os.path.join(SONIC_DIR, f"{label}.wav")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return filename, tone

def play_tone(filename):
    if not sound_enabled:
        return
    try:
        wf = wave.open(filename, 'rb')
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                         channels=wf.getnchannels(),
                         rate=wf.getframerate(),
                         output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        pa.terminate()
    except Exception as e:
        print(f"[SOUND ERROR] {e}")

# === SELF-DESTRUCT LOGIC ===
def schedule_destruction(data_type, payload):
    delay = DESTRUCT_RULES.get(data_type, 60)
    label = f"{data_type}_{int(time.time())}"
    tone_file, waveform = generate_sonic_signature(payload, label)
    with mutation_lock:
        mutation_log.append((data_type, payload, delay, waveform))
    def destroy():
        time.sleep(delay)
        print(f"[SELF-DESTRUCT] {data_type.upper()} payload destroyed: {payload}")
        play_tone(tone_file)
    threading.Thread(target=destroy, daemon=True).start()

# === MONITORS ===
def monitor_network():
    while True:
        try:
            conns = psutil.net_connections(kind='inet')
            for conn in conns:
                if conn.status == 'ESTABLISHED':
                    laddr = conn.laddr.ip if conn.laddr else None
                    raddr = conn.raddr.ip if conn.raddr else None
                    if not laddr or not raddr:
                        schedule_destruction('no_mac_ip', str(conn))
        except Exception as e:
            print(f"[NETWORK ERROR] {e}")
        time.sleep(1)

def monitor_processes():
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmd = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'backdoor' in cmd.lower():
                    schedule_destruction('backdoor', cmd)
        except Exception as e:
            print(f"[PROCESS ERROR] {e}")
        time.sleep(2)

def scan_payload(payload):
    if any(key in payload.lower() for key in PERSONAL_KEYS):
        schedule_destruction('personal', payload)

def inject_fake_telemetry():
    fake_data = json.dumps({
        'voltage': 0.0,
        'current': 0.0,
        'timestamp': str(datetime.datetime.now())
    })
    schedule_destruction('fake_telemetry', fake_data)

# === GUI ===
class ASIGuardianGUI:
    def __init__(self, root):
        self.root = root
        root.title("MagicBox ASI Guardian Shell")
        root.geometry("1200x800")
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.tree = ttk.Treeview(root, columns=('Type', 'Payload', 'Timer'), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='x', padx=10, pady=10)

        self.canvas = Canvas(root, width=600, height=150, bg='black')
        self.canvas.pack(pady=10)

        self.polarity = Canvas(root, width=600, height=150, bg='white')
        self.polarity.pack(pady=10)

        self.sound_btn = ttk.Button(root, text="Sound: ON", command=self.toggle_sound)
        self.sound_btn.pack(pady=10)

        self.timeline = Text(root, height=10, bg='lightyellow')
        self.timeline.pack(fill='both', padx=10, pady=10)

        self.update_gui()

    def toggle_sound(self):
        global sound_enabled
        sound_enabled = not sound_enabled
        self.sound_btn.config(text=f"Sound: {'ON' if sound_enabled else 'OFF'}")

    def update_gui(self):
        try:
            with mutation_lock:
                recent = mutation_log[-10:]
            self.tree.delete(*self.tree.get_children())
            for item in recent:
                self.tree.insert('', 'end', values=(item[0], item[1][:50], f"{item[2]}s"))

            self.canvas.delete("all")
            if recent:
                waveform = recent[-1][3]
                for i in range(len(waveform)-1):
                    x1 = i * 2
                    y1 = 75 - waveform[i] * 50
                    x2 = (i+1) * 2
                    y2 = 75 - waveform[i+1] * 50
                    self.canvas.create_line(x1, y1, x2, y2, fill='green')

            self.polarity.delete("all")
            for i in range(100):
                v = np.random.uniform(0.5, 1.5)
                c = np.random.uniform(0.1, 0.5)
                self.polarity.create_line(i*6, 150, i*6, 150 - v*100, fill='red')
                self.polarity.create_line(i*6+3, 150, i*6+3, 150 - c*100, fill='blue')

            self.timeline.delete('1.0', tk.END)
            for item in recent:
                self.timeline.insert(tk.END, f"[{item[0].upper()}] {item[1][:80]} → Self-destruct in {item[2]}s\n")
        except Exception as e:
            print(f"[GUI ERROR] {e}")
        self.root.after(1000, self.update_gui)

# === MAIN ===
if __name__ == '__main__':
    threading.Thread(target=monitor_network, daemon=True).start()
    threading.Thread(target=monitor_processes, daemon=True).start()
    threading.Thread(target=inject_fake_telemetry, daemon=True).start()

    root = tk.Tk()
    app = ASIGuardianGUI(root)
    root.mainloop()

