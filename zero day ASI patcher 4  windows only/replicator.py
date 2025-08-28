import json, socket

def replicate_codex(path="fusion_codex.json", target_nodes=[9001, 9002]):
    try:
        with open(path) as f:
            codex = json.load(f)
    except FileNotFoundError:
        print("⚠️ Codex not found.")
        return

    payload = json.dumps(codex[-1])  # Send latest rewrite
    for port in target_nodes:
        try:
            s = socket.socket()
            s.connect(("localhost", port))
            s.send(payload.encode())
            s.close()
            print(f"📡 Replicated to node:{port}")
        except:
            print(f"❌ Node:{port} unreachable.")

