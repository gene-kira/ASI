import psutil
from ram_cache import remove_ramdisk

def monitor_memory(threshold=0.85):
    usage = psutil.virtual_memory().percent / 100
    if usage > threshold:
        print("[Daemon] Memory pressure detected. Purging cache.")
        remove_ramdisk()

