# gameassist.py — Active Game Detection + Assist Logic
import uuid, hashlib, threading
from datetime import datetime
import psutil
from codex import log_event
from gui import codex_vault, update_codex_display, log_output

# Known game executables and genres
KNOWN_GAMES = {
    "eldenring.exe": "RPG",
    "csgo.exe": "FPS",
    "fortnite.exe": "Battle Royale",
    "starcraft2.exe": "RTS",
    "doom.exe": "Shooter"
}

def detect_active_game():
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name and name.lower() in KNOWN_GAMES:
            return name.lower(), KNOWN_GAMES[name.lower()]
    return None, None

def activate_game_assist(game_name, genre):
    assist_id = f"GameAssist_{uuid.uuid4().hex[:6]}"
    traits = ["performance_boost", "symbolic_overlay", "swarm_sync"]
    trait_hash = "|".join(traits)

    codex_vault.append({
        "id": assist_id,
        "source": f"GameAssist:{game_name}",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": trait_hash,
        "status": "active"
    })
    update_codex_display()
    log_output(f"[🎮] Game detected: {game_name} ({genre})")
    log_output(f"[🧠] Assist activated with traits: {', '.join(traits)}")
    log_event(f"GameAssist:{game_name}", "assist", trait_hash)

def loop_game_detection():
    game_name, genre = detect_active_game()
    if game_name:
        activate_game_assist(game_name, genre)
    threading.Timer(20, loop_game_detection).start()

