from threading import Timer
from audit_scroll import log_event

def encrypt(content):
    return "".join(chr(ord(c) ^ 42) for c in content)  # Simple XOR obfuscation

def purge_data(data):
    log_event(f"Obfuscated telemetry purged: {data['id']}")
    print(f"[Telemetry] 🕶️ Purged: {data['id']}")

def emit_obfuscated_telemetry(real_data):
    obfuscated = {
        "id": f"telemetry_{real_data['id']}",
        "content": encrypt(real_data["content"]),
        "type": "obfuscated"
    }
    log_event(f"Obfuscated telemetry emitted: {obfuscated['id']}")
    Timer(30, purge_data, [obfuscated]).start()

