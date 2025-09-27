import os
import io
import sys
import time
import socket
import hashlib
import threading
import platform
from datetime import datetime
from PIL import Image, UnidentifiedImageError
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# === CONFIG ===
SCAN_INTERVAL = 5  # seconds
SAFE_FORMAT = "PNG"
BLOCKED_DOMAINS = ["telemetry.example.com", "ads.example.net"]
LOG_PATH = "mutation_log.txt"
TARGET_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp", ".ico", ".svg")

# === GLOBAL STATE ===
stats = {
    "total_scanned": 0,
    "threats_detected": 0,
    "last_mutation": "Never",
    "daemon_alive": True,
    "active_mounts": []
}
hash_cache = set()

# === SYMBOLIC FEEDBACK ===
def glyph(msg, gui=None):
    stamp = f"{datetime.now()} :: {msg}"
    print(f"[🧠 GLYPH] {msg}")
    with open(LOG_PATH, "a") as f:
        f.write(stamp + "\n")
    if gui:
        gui.insert(tk.END, stamp + "\n")
        gui.see(tk.END)

# === DNS SUPPRESSION ===
def suppress_dns(gui=None):
    original_getaddrinfo = socket.getaddrinfo
    def cloaked_getaddrinfo(host, *args, **kwargs):
        if any(bad in host for bad in BLOCKED_DOMAINS):
            glyph(f"Blocked DNS resolution for {host}", gui)
            raise socket.gaierror(f"Blocked domain: {host}")
        return original_getaddrinfo(host, *args, **kwargs)
    socket.getaddrinfo = cloaked_getaddrinfo
    glyph("DNS cloak activated", gui)

# === IMAGE MUTATION ===
def process_image(path, gui=None):
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format=SAFE_FORMAT)
            data = buf.getvalue()
            hash_digest = hashlib.sha256(data).hexdigest()
            if hash_digest in hash_cache:
                return
            hash_cache.add(hash_digest)
            stats["total_scanned"] += 1
            stats["last_mutation"] = datetime.now().strftime("%H:%M:%S")
            glyph(f"Mutation lineage: {path} → SHA256:{hash_digest}", gui)
            if len(data) < 100:
                stats["threats_detected"] += 1
                glyph(f"⚠️ DAEMON TRIGGERED: anomaly detected in {path}", gui)
    except UnidentifiedImageError:
        stats["threats_detected"] += 1
        glyph(f"⚠️ Unidentified image format: {path}", gui)
    except Exception as e:
        stats["threats_detected"] += 1
        glyph(f"⚠️ Mutation error: {e}", gui)

# === SYSTEM-WIDE SCANNER ===
def get_scan_targets():
    targets = []
    user_dirs = ["Downloads", "Pictures", "Desktop", "Documents", "Temp"]
    home = os.path.expanduser("~")
    for d in user_dirs:
        path = os.path.join(home, d)
        if os.path.exists(path):
            targets.append(path)
    if platform.system() == "Windows":
        for drive in "DEFGHIJKLMNOPQRSTUVWXYZ":
            mount = f"{drive}:\\"
            if os.path.exists(mount):
                targets.append(mount)
    else:
        for mount in ["/mnt", "/media"]:
            if os.path.exists(mount):
                for sub in os.listdir(mount):
                    full = os.path.join(mount, sub)
                    if os.path.isdir(full):
                        targets.append(full)
    stats["active_mounts"] = targets
    return targets

def scan_images(gui=None):
    while True:
        try:
            for folder in get_scan_targets():
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(TARGET_EXTENSIONS):
                            full_path = os.path.join(root, file)
                            threading.Thread(target=process_image, args=(full_path, gui)).start()
            time.sleep(SCAN_INTERVAL)
        except Exception as e:
            glyph(f"⚠️ Scanner error: {e}", gui)

# === GUI DASHBOARD ===
def launch_gui():
    root = tk.Tk()
    root.title("🧠 Mutation System Guardian")
    root.geometry("900x600")

    log_box = ScrolledText(root, font=("Consolas", 10), bg="#111", fg="#0f0")
    log_box.pack(fill=tk.BOTH, expand=True)

    status_frame = tk.Frame(root, bg="#222")
    status_frame.pack(fill=tk.X)

    labels = {
        "scanned": tk.Label(status_frame, text="Images Scanned: 0", fg="#0f0", bg="#222", font=("Arial", 10)),
        "threats": tk.Label(status_frame, text="Threats Detected: 0", fg="#f00", bg="#222", font=("Arial", 10)),
        "last": tk.Label(status_frame, text="Last Mutation: Never", fg="#0ff", bg="#222", font=("Arial", 10)),
        "daemon": tk.Label(status_frame, text="Daemon Status: Alive", fg="#fff", bg="#222", font=("Arial", 10)),
        "mounts": tk.Label(status_frame, text="Active Mounts: 0", fg="#ff0", bg="#222", font=("Arial", 10))
    }

    for lbl in labels.values():
        lbl.pack(side=tk.LEFT, padx=10)

    def update_status():
        while True:
            labels["scanned"].config(text=f"Images Scanned: {stats['total_scanned']}")
            labels["threats"].config(text=f"Threats Detected: {stats['threats_detected']}")
            labels["last"].config(text=f"Last Mutation: {stats['last_mutation']}")
            labels["daemon"].config(text=f"Daemon Status: {'Alive' if stats['daemon_alive'] else 'Dead'}")
            labels["mounts"].config(text=f"Active Mounts: {len(stats['active_mounts'])}")
            time.sleep(1)

    threading.Thread(target=update_status, daemon=True).start()
    suppress_dns(log_box)
    threading.Thread(target=scan_images, args=(log_box,), daemon=True).start()
    root.mainloop()

# === ENTRY POINT ===
if __name__ == "__main__":
    launch_gui()
