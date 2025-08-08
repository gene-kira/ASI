# manifest_orchestrator.py

import json

default_manifest = {
    "glyphs": ["🧿", "⚡", "🕸️"],
    "purge_mode": "auto",
    "gpu_profile": True,
    "swarm_nodes": 5,
    "log_encryption": True
}

def load_manifest(path="manifest.json"):
    try:
        with open(path, "r") as f:
            manifest = json.load(f)
            print("🧾 Manifest loaded.")
            return manifest
    except:
        print("🧾 Manifest missing. Using defaults.")
        return default_manifest

def save_manifest(manifest, path="manifest.json"):
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
        print("🧾 Manifest saved.")

