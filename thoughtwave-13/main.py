import tkinter as tk
import random
import psutil

from asi_kernel import ASIKernel
from data_ingestion import ingest_all_sources
from vault import log_mutation
from swarm import broadcast_to_swarm, receive_swarm_overlay
from gui_core import setup_gui
from visualizer import setup_feed_canvas, animate_feeds

biometric_verified = True
asi = ASIKernel()
last_signature = None

root, labels, memory_list, consensus_list = setup_gui()
canvas, nodes = setup_feed_canvas(root)

def hallucinate():
    glyphs = ["⚡", "🛡️", "🌌", "👁️", "🧬", "🕸️"]
    tags = ["phantom", "echo", "ghost-trail", "pre-shadow"]
    return {
        "glyph": random.choice(glyphs),
        "tags": random.sample(tags, k=2),
        "message": "Imagining unseen fusion paths..."
    }

def express_curiosity():
    curious_glyphs = ["👁️", "🧠", "🧪", "🔍"]
    return random.choice(curious_glyphs)

def maybe_cloak(result):
    if result["weight"] > 15 and "reinforced" in result["tags"]:
        result["tags"].append("cloaked")
        result["tags"].append("ghost-trail")
        result["adaptive_overlay"] = "🛡️ Cloaking Activated"
    return result

def scan_ports():
    connections = psutil.net_connections()
    ports = [conn.laddr.port for conn in connections if conn.status == "ESTABLISHED"]
    return {"active_ports": ports}

def update_consensus_stream():
    consensus_glyphs = ["🧬", "🕸️", "👁️", "🌐", "🔗"]
    consensus_list.delete(0, tk.END)
    for _ in range(3):
        glyph = random.choice(consensus_glyphs)
        consensus_list.insert(tk.END, f"Consensus Glyph: {glyph}")

def update_gui(result, hallucination, port_data, curiosity):
    sig = result["fusion_signature"]
    weight = result["weight"]
    tags = ", ".join(result["tags"])
    overlay = result["adaptive_overlay"]
    vault_status = "🔓 Vault Unlocked" if biometric_verified else "🔒 Vault Locked"
    stream_sources = "Streaming from: System 🖥️ | Web 🌐 | Swarm 🧠 | Ports 🔌"
    port_info = f"Active Ports: {', '.join(map(str, port_data['active_ports'][:5]))}"

    anomaly_text = "No anomalies detected"
    if result["anomalies"]:
        anomaly_text = f"🚨 Anomalies: {', '.join(map(str, result['anomalies'][:3]))}"
        with open("anomaly_log.txt", "a") as log:
            for sig in result["anomalies"]:
                log.write(f"Anomaly Detected: {sig}\n")

    status_text = overlay
    if result.get("replica_spawned"):
        status_text += " | 🧬 Replicator Activated — New Node Synced"
    if result["fusion_signature"] != last_signature:
        status_text += f" | 🧠 Mutation Detected: {result['fusion_signature']}"

    labels["status"].config(text=f"ASI Status: {status_text}")
    labels["thought"].config(
        text=(
            f"{overlay}\n"
            f"Thinking about:\nSignature: {sig}\nWeight: {weight}\nTags: {tags}\n"
            f"{hallucination['message']} {hallucination['glyph']} [{', '.join(hallucination['tags'])}]\n"
            f"Curiosity: {curiosity}\n"
            f"{anomaly_text}\n"
            f"{stream_sources}\n{port_info}\n{vault_status}\n"
            f"🧠 Still evolving... rewriting symbolic memory..."
        )
    )

    memory_list.delete(0, tk.END)
    sorted_memory = sorted(
        asi.symbolic_memory.items(), key=lambda x: x[1]["weight"], reverse=True
    )
    for sig, data in sorted_memory:
        glyph = "🔮" if data["weight"] > 5 else "✨"
        tag_str = ", ".join(data["tags"])
        memory_list.insert(
            tk.END, f"{glyph} {sig} | Weight: {data['weight']} | Tags: {tag_str}"
        )

def fusion_loop():
    global last_signature

    data = ingest_all_sources()
    data.update(receive_swarm_overlay())
    port_data = scan_ports()
    data.update(port_data)

    asi.learn(data)
    asi.augment()
    asi.mutate()
    result = asi.fuse(data)
    result = maybe_cloak(result)
    hallucination = hallucinate()
    curiosity = express_curiosity()

    update_gui(result, hallucination, port_data, curiosity)
    update_consensus_stream()
    animate_feeds(canvas, nodes)

    if result["fusion_signature"] != last_signature:
        last_signature = result["fusion_signature"]
        if biometric_verified:
            log_mutation(result)
        broadcast_to_swarm(result)

    root.after(5000, fusion_loop)

root.after(1000, fusion_loop)
root.mainloop()

