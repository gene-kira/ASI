import json, os, time, hashlib
from cryptography.fernet import Fernet

def get_obfuscated_filename():
    seed = "mutation" + str(os.getpid()) + str(time.time())
    name = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return f".{name}.log"

LOG_FILE = get_obfuscated_filename()

def load_memory():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: return json.load(f)
    return []

def save_memory(log):
    with open(LOG_FILE, "w") as f: json.dump(log, f, indent=2)

def export_logs(log, path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    data = json.dumps(log).encode()
    encrypted = cipher.encrypt(data)
    with open(path, "wb") as f: f.write(encrypted)
    with open(path + ".key", "wb") as kf: kf.write(key)
    return key

