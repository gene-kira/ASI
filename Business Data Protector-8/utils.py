# utils.py

import time

def log_codex(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def load_memory():
    return []

def tag_data(entry, tag):
    entry["tag"] = tag
    return entry

