# replicator.py
import os
import shutil
from config import SWARM_FILE_PREFIX, SWARM_FILE_EXTENSION

def sync_mutations(local_path, swarm_path):
    if not os.path.exists(local_path) or not os.path.exists(swarm_path):
        return

    # 🔁 Push local mutations to swarm
    for file in os.listdir(local_path):
        if file.startswith(SWARM_FILE_PREFIX) and file.endswith(SWARM_FILE_EXTENSION):
            src = os.path.join(local_path, file)
            dst = os.path.join(swarm_path, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

    # 🔁 Pull swarm mutations to local
    for file in os.listdir(swarm_path):
        if file.startswith(SWARM_FILE_PREFIX) and file.endswith(SWARM_FILE_EXTENSION):
            src = os.path.join(swarm_path, file)
            dst = os.path.join(local_path, file)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

