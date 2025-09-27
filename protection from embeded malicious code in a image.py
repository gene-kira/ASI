import os
import sys
import io
import time
import socket
import signal
import subprocess
import threading
import hashlib
from PIL import Image, UnidentifiedImageError
from datetime import datetime

# === CONFIG ===
SAFE_FORMAT = 'PNG'
BLOCKED_DOMAINS = ['telemetry.example.com', 'ads.example.net']
LOG_PATH = 'mutation_log.txt'
DNS_CLOAK_ENABLED = True

# === SYMBOLIC FEEDBACK ===
def glyph(msg):
    print(f"[🛡️ GLYPH] {msg}")
    with open(LOG_PATH, 'a') as f:
        f.write(f"{datetime.now()} :: {msg}\n")

# === DNS SUPPRESSION ===
def suppress_dns():
    if not DNS_CLOAK_ENABLED:
        return
    glyph("Activating DNS cloak...")
    original_getaddrinfo = socket.getaddrinfo

    def cloaked_getaddrinfo(host, *args, **kwargs):
        if any(bad in host for bad in BLOCKED_DOMAINS):
            glyph(f"Blocked DNS resolution for {host}")
            raise socket.gaierror(f"Blocked domain: {host}")
        return original_getaddrinfo(host, *args, **kwargs)

    socket.getaddrinfo = cloaked_getaddrinfo

# === IMAGE SANDBOX ===
def decode_image_sandbox(path):
    def worker(pipe_out):
        try:
            with Image.open(path) as img:
                img = img.convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format=SAFE_FORMAT)
                pipe_out.write(buf.getvalue())
                glyph(f"Image re-encoded to {SAFE_FORMAT} safely.")
        except UnidentifiedImageError:
            glyph("Failed to identify image format.")
        except Exception as e:
            glyph(f"Sandbox error: {e}")

    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.setsid()
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        os.close(r)
        worker(os.fdopen(w, 'wb'))
        os._exit(0)
    else:
        os.close(w)
        data = os.fdopen(r, 'rb').read()
        glyph(f"Sandboxed decoding complete. Bytes: {len(data)}")
        return data

# === MUTATION LINEAGE ===
def log_mutation(path, data):
    hash_digest = hashlib.sha256(data).hexdigest()
    glyph(f"Mutation lineage: {path} → SHA256:{hash_digest}")

# === MAIN ENTRY ===
def process_image(path):
    glyph(f"Processing image: {path}")
    suppress_dns()
    data = decode_image_sandbox(path)
    log_mutation(path, data)
    glyph("Mutation complete. Image is safe for AI ingestion.")

# === TEST HOOK ===
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mutation_image_guard.py <image_path>")
        sys.exit(1)
    process_image(sys.argv[1])
