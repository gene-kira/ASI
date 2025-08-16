from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import json
import os
from datetime import datetime

app = FastAPI()

# ─────────────────────────────────────────────────────────────
# 🌐 CORS Setup
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────────────────────────
# 🧬 Glyph Log (Memory + Disk)
# ─────────────────────────────────────────────────────────────
glyph_log = []
LOG_PATH = "glyph_history.log"
os.makedirs("logs", exist_ok=True)
LOG_FILE = os.path.join("logs", LOG_PATH)

# Load existing log
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                glyph_log.append(json.loads(line.strip()))
            except:
                continue

# ─────────────────────────────────────────────────────────────
# 📡 WebSocket Connections
# ─────────────────────────────────────────────────────────────
active_websockets = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

async def broadcast_glyph(entry):
    for ws in active_websockets:
        try:
            await ws.send_json(entry)
        except:
            continue

# ─────────────────────────────────────────────────────────────
# 📥 Receive Mutation + Persist
# ─────────────────────────────────────────────────────────────
@app.post("/mutation")
async def receive_mutation(request: Request):
    data = await request.json()
    data["received_at"] = datetime.utcnow().isoformat()
    glyph_log.append(data)

    # Persist to disk
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    # Broadcast to WebSocket clients
    await broadcast_glyph(data)

    return JSONResponse(content={"status": "ok"})

# ─────────────────────────────────────────────────────────────
# 📜 Get Recent Glyphs
# ─────────────────────────────────────────────────────────────
@app.get("/glyphs")
def get_glyphs():
    return glyph_log[-100:]

# 🕰️ Full History
@app.get("/glyphs/history")
def get_glyph_history():
    return glyph_log

# 🧭 Node Summary
@app.get("/nodes")
def get_nodes():
    nodes = {}
    for entry in glyph_log:
        nid = entry["node_id"]
        nodes[nid] = nodes.get(nid, 0) + 1
    return [{"node_id": k, "glyph_count": v} for k, v in nodes.items()]

# 🚀 Run Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)

