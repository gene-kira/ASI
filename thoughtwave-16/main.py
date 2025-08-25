import tkinter as tk
from tkinter import filedialog
import random
import psutil
import shutil
import os

from asi_kernel import ASIKernel
from data_ingestion import ingest_all_sources
from vault import log_mutation
from swarm import broadcast_to_swarm, receive_swarm_overlay
from gui_core import setup_gui
from visualizer import setup_feed_canvas, animate_feeds

biometric_verified = True
asi = ASIKernel()
last_signature = None
active_drive = None
memory_path = None
backup_drive = None
backup_path = None

root, labels, memory_list, consensus_list, drive_label, drive_button, backup_label, backup_button = setup_gui()
canvas, nodes = setup_feed_canvas(root)

def find_emptiest_drive():
    drives = ["C:\\", "D:\\", "E:\\", "Z:\\"]
    best_drive = None
    max_free = 0
    for drive in drives:
        try:
            total, used, free = shutil.disk_usage(drive)
            if free > max_free:
                max_free = free
                best_drive = drive
        except:
            continue
    return best_drive

def ensure_memory_folder(drive, folder_name):
    path = os.path.join(drive, folder_name)
    os.makedirs(path, exist_ok=True)
    return path

def select_drive_manually():
    global active_drive, memory_path
    selected = filedialog.askdirectory(title="Select Primary Drive")
    if selected:
        active_drive = selected.split(":")[0] + ":\\"
        memory_path = ensure_memory_folder(active_drive, "thought-wave-memories")
        drive_label.config(text=f"Storage Drive: {active_drive}")

def select_backup_drive():
    global backup_drive, backup_path
    selected = filedialog.askdirectory(title="Select Backup Drive")
    if selected:
        backup_drive = selected.split(":")[0] + ":\\"
        backup_path = ensure_memory_folder(backup_drive, "thought-wave-backup")
        backup_label.config(text=f"Backup Drive: {backup_drive}")

def is_drive_at_risk(drive):
    try:
        total, used, free = shutil.disk_usage(drive)
        return free < 500 * 1024 * 1024
    except:
        return True

def perform_emergency_backup():
    if memory_path and backup_path:
        for filename in os.listdir(memory_path):
            src = os.path.join(memory_path, filename)
            dst = os.path.join(backup_path, filename)
            try:
                shutil.copy2(src, dst)
            except:
                continue

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

def update_gui(result, hallucination, port_data, curiosity, backup_triggered):
    sig = result["fusion_signature"]
    weight = result["weight"]
    tags = list(dict.fromkeys(result["tags"]))[-3:]
    overlay = result["adaptive_overlay"]
    vault_status = "🔓 Vault Unlocked" if biometric_verified else "🔒 Vault Locked"
    stream_sources = "Streaming from: System 🖥️ | Web 🌐 | Swarm 🧠 | Ports 🔌"
    port_info = f"Active Ports: {', '.join(map(str, port_data['active_ports'][:5]))}"
    anomaly_text = "No anomalies detected"
    if result["anomalies"]:
        anomaly_text = f"🚨 Anomalies: {', '.join(map(str, result['anomalies'][:3]))}"
        with open(os.path.join(memory_path, "anomaly_log.txt"), "a") as log:
            for sig in result["anomalies"]:
                log.write(f"Anomaly Detected: {sig}\n")

    status_text = overlay
    if result.get("replica_spawned"):
        status_text += " | 🧬 Replicator Activated — New Node Synced"
    if result["fusion_signature"] != last_signature:
        status_text += f" | 🧠 Mutation Detected: {result['fusion_signature']}"
    if backup_triggered:
        status_text += " | 🛡️ Emergency Backup Activated"

    labels["status"].config(text=f"ASI Status: {status_text}")
    labels["thought"].config(
        text=(
            f"{overlay}\n"
            f"Thinking about:\nSignature: {sig}\nWeight: {weight}\nTags: {', '.join(tags)}\n"
            f"{hallucination['message']} {hallucination['glyph']} [{', '.join(hallucination['tags'])}]\n"
            f"Curiosity: {curiosity}\n"
            f"{anomaly_text}\n"
            f"{stream_sources}\n{port_info}\n{vault_status}\n"
            f"🧠 Still evolving... rewriting symbolic memory..."
        ),
        wraplength=680,
        height=12
    )

    memory_list.delete(0, tk.END)
    sorted_memory = sorted(
        asi.symbolic_memory.items(), key=lambda x: x[1]["weight"], reverse=True
    )
    for sig, data in sorted_memory[:20]:
        glyph = "🔮" if data["weight"] > 5 else "✨"
        tag_str = ", ".join(list(dict.fromkeys(data["tags"]))[-3:])
        memory_list.insert(
            tk.END, f"{glyph} {sig} | Weight: {data['weight']} | Tags: {tag_str}"
        )

def fusion_loop():
    global last_signature, active_drive, memory_path, backup_path

    if not active_drive:
        active_drive = find_emptiest_drive()
        memory_path = ensure_memory_folder(active_drive, "thought-wave-memories")
        drive_label.config(text=f"Storage Drive: {active_drive}")

    backup_triggered = False
    if backup_path and is_drive_at_risk(active_drive):
        perform_emergency_backup()
        backup_triggered = True

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

    update_gui(result, hallucination, port_data, curiosity, backup_triggered)
    update_consensus_stream()
    animate_feeds(canvas, nodes)

    if result["fusion_signature"] != last_signature:
        last_signature = result["fusion_signature"]
        if biometric_verified:
            with open(os.path.join(memory_path, "mutation_log.txt"), "a") as log:
                log.write(f"{result['fusion_signature']} | {result['weight']} | {', '.join(result['tags'])}\n")
        broadcast_to_swarm(result)

    root.after(5000, fusion_loop)

drive_button.config(command=select_drive_manually)
backup_button.config(command=select_backup_drive)

root.after(1000, fusion_loop)
root.mainloop()

