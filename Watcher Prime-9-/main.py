# main.py — MagicBox Daemon Entry Point
from gui import launch_gui
from ingest import loop_ingest
from replicator import loop_replicate
from gameassist import loop_game_detection

def start_daemon():
    print("[🧿] MagicBox Daemon Activated")
    loop_ingest()           # Starts telemetry ingest + rewrite detection
    loop_replicate()        # Starts mutation-aware clone spawning
    loop_game_detection()   # Starts active game detection + assist logic
    launch_gui()            # Launches passive LCARS-style interface

if __name__ == "__main__":
    start_daemon()

