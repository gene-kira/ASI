# gameassist.py — Active Game Detection + Assist Logic
import uuid, hashlib, threading, json, os
from datetime import datetime
import psutil
from codex import log_event
from gui import codex_vault, update_codex_display, log_output

GAME_DB_FILE = "game_db.json"

def load_known_games():
    if os.path.exists(GAME_DB_FILE):
        with open(GAME_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_known_game(exe_name, genre):
    games = load_known_games()
    games[exe_name.lower()] = genre
    with open(GAME_DB_FILE, "w") as f:
        json.dump(games, f, indent=2)
    log_output(f"[🎮] Registered new game: {exe_name} ({genre})")

def detect_active_game():
    known_games = load_known_games()
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name and name.lower() in known_games:
            return name.lower(), known_games[name.lower()]
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

