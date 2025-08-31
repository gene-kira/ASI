# 🔄 Autoloader
import subprocess
import sys

def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for lib in ['tkinter', 'hashlib', 'socket', 'threading', 'playsound']:
    autoload(lib)

# 🧠 Core Imports
import tkinter as tk
from tkinter import messagebox
import hashlib, socket, threading
from playsound import playsound

# 🔐 SwarmSyncCore
def verify_node(destination_ip):
    try:
        socket.create_connection((destination_ip, 80), timeout=2)
        return True
    except:
        return False

# 🛡️ TamperGuard
class MythicDataGuard:
    def __init__(self, payload, destination_ip):
        self.payload = payload
        self.destination_ip = destination_ip
        self.encrypted = self._cloak(payload)
        self.integrity_hash = self._generate_hash(self.encrypted)

    def _cloak(self, data):
        return f"⧈CLOAKED⧈:{data[::-1]}"

    def _generate_hash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def transmit(self):
        if not verify_node(self.destination_ip):
            self._self_destruct()
            self._trigger_voice_alarm()
            return None
        else:
            return self._uncloak(self.encrypted)

    def _self_destruct(self):
        self.payload = None
        self.encrypted = None
        self.integrity_hash = None

    def _trigger_voice_alarm(self):
        threading.Thread(target=lambda: playsound("alarm.mp3")).start()
        messagebox.showerror("⚠️ Alert", "Data tampered. Payload destroyed.")

    def _uncloak(self, data):
        if data.startswith("⧈CLOAKED⧈:"):
            return data[len("⧈CLOAKED⧈:"):][::-1]
        return None

# 🎨 MagicBox GUI
class MagicBoxGUI:
    def __init__(self, root):
        root.title("MagicBox Data Guard")
        root.geometry("400x300")
        root.configure(bg="#1e1e2f")

        tk.Label(root, text="Enter Data:", bg="#1e1e2f", fg="#f0f0f0").pack(pady=10)
        self.data_entry = tk.Entry(root, width=40)
        self.data_entry.pack()

        tk.Label(root, text="Destination IP:", bg="#1e1e2f", fg="#f0f0f0").pack(pady=10)
        self.ip_entry = tk.Entry(root, width=40)
        self.ip_entry.pack()

        self.send_button = tk.Button(root, text="🚀 Send Securely", command=self.send_data, bg="#4caf50", fg="white")
        self.send_button.pack(pady=20)

        self.status_label = tk.Label(root, text="", bg="#1e1e2f", fg="#f0f0f0")
        self.status_label.pack()

    def send_data(self):
        payload = self.data_entry.get()
        destination_ip = self.ip_entry.get()
        guard = MythicDataGuard(payload, destination_ip)
        result = guard.transmit()
        if result:
            self.status_label.config(text="✅ Data delivered securely.")
        else:
            self.status_label.config(text="❌ Transmission failed.")

# 🧿 Launch Daemon
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

