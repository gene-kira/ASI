from datetime import datetime
from codex import log_event

# 🎭 Persona Definitions
PERSONAS = {
    "Gaming": {"name": "SquadSyncBot", "color": "#ff9900"},
    "Finance": {"name": "LedgerPhantom", "color": "#33cc33"},
    "Medical": {"name": "PulseEcho", "color": "#cc66ff"},
    "Social": {"name": "GhostContact", "color": "#66cccc"},
    "Default": {"name": "NullPacket", "color": "#999999"}
}

TEXT_COLOR = "#c5c6c7"

def detect_genre(streams):
    labels = " ".join([s["iface"].lower() for s in streams])
    if any(k in labels for k in ["game", "steam", "epic"]): return "Gaming"
    if any(k in labels for k in ["bank", "finance", "ledger"]): return "Finance"
    if any(k in labels for k in ["med", "pulse", "bio"]): return "Medical"
    if any(k in labels for k in ["social", "msg", "chat"]): return "Social"
    return "Default"

def inject_decoy_persona(canvas, genre):
    persona = PERSONAS.get(genre, PERSONAS["Default"])
    color = persona["color"]
    name = persona["name"]

    ring = canvas.create_oval(
        180, 105, 220, 145,
        outline=color, width=2
    )
    text = canvas.create_text(
        200, 155,
        text=name, fill=TEXT_COLOR, font=("Helvetica", 6, "italic")
    )
    canvas.after(30000, lambda: canvas.delete(ring) or canvas.delete(text))

    entry = {
        "event": "decoy_persona_discarded",
        "persona": name,
        "genre": genre,
        "reason": "expired 30s lifecycle",
        "timestamp": datetime.now().isoformat()
    }
    log_event(entry)
    print(f"[🕵️] Decoy persona '{name}' injected for genre '{genre}'")

