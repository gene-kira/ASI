import os
import json

CODEX_FILE = "fusion_codex.json"

def log_event(entry):
    """
    Logs a general event to the codex.
    """
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            try:
                codex = json.load(f)
            except json.JSONDecodeError:
                codex = []
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

def log_mutation(mutation_entry):
    """
    Logs a mutation rewrite event to the codex.
    """
    mutation_entry["event"] = "asi_mutation_rewrite"
    log_event(mutation_entry)

