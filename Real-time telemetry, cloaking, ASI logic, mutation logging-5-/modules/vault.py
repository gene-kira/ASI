# === VeilMind Nexus — vault.py ===
# Purpose: Store encrypted mutations, symbolic memory, and emotional telemetry

import time  # ✅ Required for timestamping mutations

# 🧠 Symbolic memory: shared across all daemons
symbolic_memory = {
    "ip_pulse": [],       # Fused telemetry snapshots
    "mutations": [],      # Mutation IDs from cloaking
    "emotions": [],       # Emotional states from ASI logic
    "anomalies": []       # Logged anomalies and integrity failures
}

# 🔐 Mutation Vault: stores encrypted payloads with metadata
mutation_vault = []

def store_mutation(encoded, mutation_id, emotion):
    vault_entry = {
        "id": mutation_id,
        "payload": encoded,
        "emotion": emotion,
        "timestamp": time.time()
    }
    mutation_vault.append(vault_entry)

