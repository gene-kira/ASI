import sys, subprocess, os, time, threading, json, random, math, socket, re, ctypes
from collections import Counter

# === Auto-Elevation ===
def require_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("🔐 Elevation required. Relaunching as admin...")
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit(0)

# === Autoloader ===
def autoload():
    print("[⚙️ Autoloader] Checking dependencies...")
    try:
        import win32evtlog
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    print("[✅] Dependencies loaded.")

# === FlowPulse Class ===
class FlowPulse:
    def __init__(self, entropy):
        self.entropy = entropy

# === Swarm Voting ===
def node_vote(patch_id):
    return random.choice([True, True, False])

def swarm_vote(patch_id, node_ids):
    votes = {}
    for nid in node_ids:
        votes[f"node{nid}"] = node_vote(patch_id)
    approved = sum(votes.values()) > len(votes) // 2
    return {"votes": votes, "approved": approved}

# === Rewrite Logic ===
CODEX_FILE = "fusion_codex.json"

def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote(entropy):
    votes = [random.choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = random.randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            try:
                codex = json.load(f)
            except:
                codex = []
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# === Codex Visualizer ===
def visualize_codex(path=CODEX_FILE, limit=5):
    if not os.path.exists(path):
        print("⚠️ Fusion codex not found.")
        return
    try:
        with open(path, "r") as f:
            codex = json.load(f)
    except:
        print("⚠️ Codex file unreadable.")
        return
    print("\n🌌 Fusion Codex Snapshot:")
    for entry in codex[-limit:]:
        print(f"🔁 Logic: {entry.get('logic', '—')}")
        print(f"🕒 Timestamp: {entry.get('timestamp', '—')}")
        print(f"🧠 Trigger: {entry.get('trigger', '—')}")
        print(f"🐝 Consensus: {entry.get('consensus', '—')}\n")

# === Replicator Agent ===
def replicate_codex(path=CODEX_FILE, target_nodes=[9001, 9002]):
    if not os.path.exists(path):
        print("⚠️ Codex not found.")
        return
    try:
        with open(path, "r") as f:
            codex = json.load(f)
    except:
        print("⚠️ Codex unreadable.")
        return
    payload = json.dumps(codex[-1])
    for port in target_nodes:
        try:
            s = socket.socket()
            s.connect(("localhost", port))
            s.send(payload.encode())
            s.close()
            print(f"📡 Replicated to node:{port}")
        except:
            print(f"❌ Node:{port} unreachable.")

# === Windows Event Monitor (Event ID 4688) ===
def start_windows_event_monitor(callback):
    import win32evtlog
    SECURITY_LOG = "Security"
    EVENT_ID = 4688

    print("🧠 Windows Event Monitor started (Security Log, Event ID 4688)")
    server = None
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    while True:
        try:
            handle = win32evtlog.OpenEventLog(server, SECURITY_LOG)
            events = win32evtlog.ReadEventLog(handle, flags, 0)
            for record in events:
                if record.EventID == EVENT_ID and record.StringInserts:
                    data = record.StringInserts
                    if len(data) >= 6:
                        try:
                            pid = int(re.search(r"\d+", data[4]).group())
                            comm = data[5]
                            event = {
                                "pid": pid,
                                "comm": comm,
                                "syscall_id": "execve",
                                "timestamp": record.TimeGenerated.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            callback(event)
                        except:
                            continue
            time.sleep(1)
        except Exception as e:
            print(f"[⚠️] Event monitor error: {e}")
            time.sleep(5)

# === ASI Threat Handler ===
pulse_buffer = []

def handle_event(event):
    feedback = f"[{event['pid']}] ⚡️ {event['syscall_id']} → {event['comm']}"
    print(feedback)

    patch_id = f"patch_{event['pid']}_{event['syscall_id']}"
    node_ids = [0, 1, 2]
    vote_result = swarm_vote(patch_id, node_ids)

    print("🐝 Swarm Consensus:")
    for node, vote in vote_result["votes"].items():
        symbol = "✅" if vote else "❌"
        print(f"  {node}: {symbol}")

    if vote_result["approved"]:
        print(f"✅ Patch {patch_id} deployed.\n")
    else:
        print(f"❌ Patch {patch_id} rejected by swarm.\n")

    entropy = round(6.0 + (event['pid'] % 3), 2)
    pulse_buffer.append(FlowPulse(entropy))

    if detect_density_spike(pulse_buffer):
        print("🔺 Symbolic density spike detected.")
        if initiate_mutation_vote(entropy):
            rewrite = rewrite_optimization_logic()
            store_rewrite_codex(rewrite)
            print(f"[📜 Codex] Rewrite stored: {rewrite['logic']}\n")
            visualize_codex()
            replicate_codex()

# === Main Bootstrap ===
def main():
    require_admin()
    autoload()
    threading.Thread(target=start_windows_event_monitor, args=(handle_event,), daemon=True).start()
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()

