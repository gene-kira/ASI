# replicator.py
import os
import shutil
import time
from config import SWARM_FILE_PREFIX, SWARM_FILE_EXTENSION
from voice import narrate_swarm_sync

def sync_mutations(local_path, swarm_path, alert_callback=None):
    if not os.path.exists(local_path) or not os.path.exists(swarm_path):
        return

    new_mutations = []

    # Incoming sync
    for file in os.listdir(swarm_path):
        if file.startswith(SWARM_FILE_PREFIX) and file.endswith(SWARM_FILE_EXTENSION):
            src = os.path.join(swarm_path, file)
            dst = os.path.join(local_path, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                new_mutations.append(file)

    # Outgoing sync
    for file in os.listdir(local_path):
        if file.startswith(SWARM_FILE_PREFIX) and file.endswith(SWARM_FILE_EXTENSION):
            src = os.path.join(local_path, file)
            dst = os.path.join(swarm_path, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

    if new_mutations and alert_callback:
        for m in new_mutations:
            timestamp = time.strftime("%H:%M:%S")
            alert_callback(f"{m} [{timestamp}]")
        narrate_swarm_sync()

