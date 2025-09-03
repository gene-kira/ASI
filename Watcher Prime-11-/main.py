# main.py — MagicBox Daemon Entry Point
from gui import launch_gui
from ingest import loop_ingest
from replicator import loop_replicate
from gameassist import loop_game_detection
from swarm import loop_swarm_sync

def start_daemon():
    print("[🧿] MagicBox Daemon Activated")
    loop_ingest()           # Telemetry ingest + rewrite detection
    loop_replicate()        # Clone spawning + trait sync
    loop_game_detection()   # Game detection + assist overlays
    loop_swarm_sync()       # Swarm sync pulses + status echo
    launch_gui()            # Mythic interface

if __name__ == "__main__":
    start_daemon()

