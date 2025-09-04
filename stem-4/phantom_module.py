import time
import json
import random
import os

PHANTOM_LOG = "phantom_manifest.json"

def spawn_phantom_module(trigger, context):
    phantom_id = f"phantom_{random.randint(1000, 9999)}"
    phantom = {
        "id": phantom_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": trigger,
        "context": context,
        "status": "active",
        "lifespan": random.randint(30, 120),  # seconds
        "reroute_logic": f"divert from {context.get('target', 'unknown')}"
    }

    print(f"[🜆 Phantom] Spawned {phantom_id} to reroute logic.")
    store_phantom_manifest(phantom)
    return phantom

def store_phantom_manifest(entry):
    manifest = []
    if os.path.exists(PHANTOM_LOG):
        with open(PHANTOM_LOG, "r") as f:
            manifest = json.load(f)
    manifest.append(entry)
    with open(PHANTOM_LOG, "w") as f:
        json.dump(manifest, f, indent=2)

def cleanup_expired_phantoms():
    if not os.path.exists(PHANTOM_LOG):
        return
    with open(PHANTOM_LOG, "r") as f:
        manifest = json.load(f)
    now = time.time()
    updated = []
    for phantom in manifest:
        created = time.mktime(time.strptime(phantom["timestamp"], "%Y-%m-%dT%H:%M:%S"))
        if now - created < phantom["lifespan"]:
            updated.append(phantom)
        else:
            print(f"[🜆 Phantom] Expired {phantom['id']}")
    with open(PHANTOM_LOG, "w") as f:
        json.dump(updated, f, indent=2)

def start_phantom_manager():
    while True:
        cleanup_expired_phantoms()
        time.sleep(10)

