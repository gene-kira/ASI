# main.py — MagicBox Daemon Entry Point
import threading
from gui import launch_gui
from ingest import loop_ingest
from replicator import loop_replicate
from gameassist import loop_game_detection

def start_daemon():
    print("[🧿] MagicBox Daemon Activated")
    loop_ingest()
    loop_replicate()
    loop_game_detection()
    launch_gui()

if __name__ == "__main__":
    start_daemon()

