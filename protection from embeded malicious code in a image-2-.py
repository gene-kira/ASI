import os
import io
import sys
import signal
import socket
import hashlib
import threading
from datetime import datetime
from PIL import Image, UnidentifiedImageError
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# === CONFIG ===
SAFE_FORMAT = 'PNG'
BLOCKED_DOMAINS = ['telemetry.example.com', 'ads.example.net']
LOG_PATH = 'mutation_log.txt'
DNS_CLOAK_ENABLED = True

# === SYMBOLIC FEEDBACK ===
def glyph(msg, gui=None):
    stamp = f"{datetime.now()} :: {msg}"
    print(f"[🧠 GLYPH] {msg}")
    with open(LOG_PATH, 'a') as f:
        f.write(stamp + "\n")
    if gui:
        gui.insert(tk.END, stamp + "\n")
        gui.see(tk.END)

# === DNS SUPPRESSION ===
def suppress_dns(gui=None):
    if not DNS_CLOAK_ENABLED:
        return
    glyph("Activating DNS cloak...", gui)
    original_getaddrinfo = socket.getaddrinfo

    def cloaked_getaddrinfo(host, *args, **kwargs):
        if any(bad in host for bad in BLOCKED_DOMAINS):
            glyph(f"Blocked DNS resolution for {host}", gui)
            raise socket.gaierror(f"Blocked domain: {host}")
        return original_getaddrinfo(host, *args, **kwargs)

    socket.getaddrinfo = cloaked_getaddrinfo

# === IMAGE SANDBOX ===
def decode_image_sandbox(path, gui=None):
    try:
        with Image.open(path) as img:
            img = img.convert('RGB')
            buf = io.BytesIO()
            img.save(buf, format=SAFE_FORMAT)
            glyph(f"Image re-encoded to {SAFE_FORMAT} safely.", gui)
            return buf.getvalue()
    except UnidentifiedImageError:
        glyph("Failed to identify image format.", gui)
        return b''
    except Exception as e:
        glyph(f"Sandbox error: {e}", gui)
        return b''

# === MUTATION LINEAGE ===
def log_mutation(path, data, gui=None):
    hash_digest = hashlib.sha256(data).hexdigest()
    glyph(f"Mutation lineage: {path} → SHA256:{hash_digest}", gui)

# === DAEMON TRIGGER ===
def trigger_daemon(path, gui=None):
    glyph(f"⚠️ DAEMON TRIGGERED: anomaly detected in {path}", gui)
    messagebox.showwarning("Daemon Trigger", f"Anomaly detected in {path}. Mutation escalation initiated.")

# === PROCESS IMAGE ===
def process_image(path, gui=None):
    glyph(f"Processing image: {path}", gui)
    suppress_dns(gui)
    data = decode_image_sandbox(path, gui)
    if not data or len(data) < 100:
        trigger_daemon(path, gui)
    else:
        log_mutation(path, data, gui)
        glyph("Mutation complete. Image is safe for AI ingestion.", gui)

# === GUI SHELL ===
def launch_gui():
    root = tk.Tk()
    root.title("🧠 Mutation Cognition Shell")
    root.geometry("700x500")

    log_box = ScrolledText(root, font=("Consolas", 10), bg="#111", fg="#0f0")
    log_box.pack(fill=tk.BOTH, expand=True)

    def select_and_process():
        path = filedialog.askopenfilename(title="Select Image")
        if path:
            threading.Thread(target=process_image, args=(path, log_box)).start()

    btn = tk.Button(root, text="🧠 Select Image for Mutation", command=select_and_process, font=("Arial", 12), bg="#222", fg="#fff")
    btn.pack(pady=10)

    root.mainloop()

# === ENTRY POINT ===
if __name__ == "__main__":
    launch_gui()
