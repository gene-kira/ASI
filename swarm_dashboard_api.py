from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from datetime import datetime

app = FastAPI()

# ─────────────────────────────────────────────────────────────
# 🌐 CORS Setup (Allow frontend access)
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────────────────────────
# 🧬 In-Memory Glyph Log
# ─────────────────────────────────────────────────────────────
glyph_log = []

# ─────────────────────────────────────────────────────────────
# 📡 Receive Mutation Events
# ─────────────────────────────────────────────────────────────
@app.post("/mutation")
async def receive_mutation(request: Request):
    data = await request.json()
    data["received_at"] = datetime.utcnow().isoformat()
    glyph_log.append(data)
    return JSONResponse(content={"status": "ok"})

# ─────────────────────────────────────────────────────────────
# 📜 Get Recent Glyphs (for dashboard)
# ─────────────────────────────────────────────────────────────
@app.get("/glyphs")
def get_glyphs():
    return glyph_log[-100:]  # Last 100 glyph events

# ─────────────────────────────────────────────────────────────
# 🕰️ Get Full Glyph History (for replay)
# ─────────────────────────────────────────────────────────────
@app.get("/glyphs/history")
def get_glyph_history():
    return glyph_log  # Full mutation trail

# ─────────────────────────────────────────────────────────────
# 🧭 Get Node Summary
# ─────────────────────────────────────────────────────────────
@app.get("/nodes")
def get_nodes():
    nodes = {}
    for entry in glyph_log:
        nid = entry["node_id"]
        nodes[nid] = nodes.get(nid, 0) + 1
    return [{"node_id": k, "glyph_count": v} for k, v in nodes.items()]

# ─────────────────────────────────────────────────────────────
# 🚀 Run Server
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)

