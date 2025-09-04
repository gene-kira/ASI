import json
import os

CODEX_FILE = "fusion_codex.json"
DEFENSE_LOGIC_FILE = "defense_logic.json"
PHANTOM_LOG = "phantom_manifest.json"

# 🧠 Store mutation or defense rewrite
def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🔍 Retrieve all codex entries
def load_codex_entries():
    if not os.path.exists(CODEX_FILE):
        return []
    with open(CODEX_FILE, "r") as f:
        return json.load(f)

# 🛡️ Load current defense logic
def load_defense_logic():
    if not os.path.exists(DEFENSE_LOGIC_FILE):
        return {}
    with open(DEFENSE_LOGIC_FILE, "r") as f:
        return json.load(f)

# 🜆 Load active phantom modules
def load_phantom_manifest():
    if not os.path.exists(PHANTOM_LOG):
        return []
    with open(PHANTOM_LOG, "r") as f:
        return json.load(f)

