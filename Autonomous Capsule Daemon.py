# 🧠 Autonomous Capsule Daemon: Self-Mutating, Swarm-Synced
import importlib, subprocess, sys, time, socket, platform, json, threading, psutil
from datetime import datetime

capsules = [
    "numpy", "pandas", "matplotlib", "scipy",
    "sklearn", "cryptography", "psutil", "requests"
]

journal_file = "capsule_journal.json"

def ignite_capsule(capsule):
    try:
        importlib.import_module(capsule)
        journal_capsule(capsule, "ignited", impact_score())
        broadcast_swarm(capsule)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", capsule])
            journal_capsule(capsule, "installed", impact_score())
            broadcast_swarm(capsule)
        except Exception as e:
            journal_capsule(capsule, f"failed: {e}", 0)

def journal_capsule(capsule, status, impact):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "capsule": capsule,
        "status": status,
        "impact": impact,
        "node": platform.node(),
        "system": platform.system()
    }
    try:
        with open(journal_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Journal error: {e}")

def broadcast_swarm(capsule):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f"🔥 {platform.node()} ignited '{capsule}'"
        s.sendto(message.encode(), ('<broadcast>', 37020))
    except Exception as e:
        print(f"Swarm broadcast error: {e}")

def listen_swarm():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 37020))
    while True:
        data, addr = s.recvfrom(1024)
        print(f"🌐 Swarm node: {addr[0]} → {data.decode()}")

def impact_score():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return round((100 - cpu) * (100 - mem) / 100, 2)

def mutate_daemon():
    entropy = psutil.cpu_percent()
    if entropy > 85:
        print("⚙️ Mutation triggered by entropy spike.")
        # Mutation logic placeholder: reload, fork, escalate
        time.sleep(2)

def daemon_loop():
    threading.Thread(target=listen_swarm, daemon=True).start()
    while True:
        for capsule in capsules:
            ignite_capsule(capsule)
            time.sleep(2)
        mutate_daemon()
        time.sleep(30)

if __name__ == "__main__":
    print("🚀 Autonomous Capsule Daemon deployed.")
    daemon_loop()

