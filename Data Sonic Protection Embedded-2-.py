import os, time, threading, socket, psutil, datetime, json
import tkinter as tk
from tkinter import ttk
import wave, pyaudio
import numpy as np

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
sound_enabled = True  # Global toggle

# === SONIC SIGNATURE GENERATION ===
def generate_sonic_signature(payload, label):
    tone_freq = sum(ord(c) for c in payload) % 1000 + 300  # 300–1300 Hz
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
    return filename

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
    tone_file = generate_sonic_signature(payload, label)
    def destroy():
        time.sleep(delay)
        print(f"[SELF-DESTRUCT] {data_type.upper()} payload destroyed: {payload}")
        play_tone(tone_file)
    threading.Thread(target=destroy, daemon=True).start()

# === NETWORK MONITOR ===
def monitor_network():
    while True:
        conns = psutil.net_connections(kind='inet')
        for conn in conns:
            if conn.status == 'ESTABLISHED':
                laddr = conn.laddr.ip if conn.laddr else None
                raddr = conn.raddr.ip if conn.raddr else None
                if not laddr or not raddr:
                    schedule_destruction('no_mac_ip', str(conn))
        time.sleep(1)

# === PROCESS MONITOR ===
def monitor_processes():
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = ' '.join(proc.info['cmdline'])
                if 'backdoor' in cmd.lower():
                    schedule_destruction('backdoor', cmd)
            except Exception:
                continue
        time.sleep(2)

# === PERSONAL DATA FILTER ===
def scan_payload(payload):
    if any(key in payload.lower() for key in PERSONAL_KEYS):
        schedule_destruction('personal', payload)

# === FAKE TELEMETRY INJECTION ===
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
        root.title("ASI Guardian Shell – Sovereign Defense Cortex")
        root.geometry("1000x600")

        self.tree = ttk.Treeview(root, columns=('Type', 'Payload', 'Timer'), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill='both', expand=True)

        self.sound_button = tk.Button(root, text="Sound: ON", command=self.toggle_sound)
        self.sound_button.pack(pady=10)

        self.update_gui()

    def toggle_sound(self):
        global sound_enabled
        sound_enabled = not sound_enabled
        self.sound_button.config(text=f"Sound: {'ON' if sound_enabled else 'OFF'}")

    def update_gui(self):
        self.tree.delete(*self.tree.get_children())
        now = datetime.datetime.now().strftime('%H:%M:%S')
        for dtype, delay in DESTRUCT_RULES.items():
            self.tree.insert('', 'end', values=(dtype, f"Live scan @ {now}", f"{delay}s"))
        root.after(1000, self.update_gui)

# === MAIN ===
if __name__ == '__main__':
    threading.Thread(target=monitor_network, daemon=True).start()
    threading.Thread(target=monitor_processes, daemon=True).start()
    threading.Thread(target=inject_fake_telemetry, daemon=True).start()

    root = tk.Tk()
    app = ASIGuardianGUI(root)
    root.mainloop()

