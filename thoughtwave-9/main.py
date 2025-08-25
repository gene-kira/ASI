import tkinter as tk
from tkinter import messagebox

from asi_kernel import ASIKernel
from data_ingestion import ingest_all_sources
from vault import log_mutation
from swarm import broadcast_to_swarm, receive_swarm_overlay
from gui_core import setup_gui
from visualizer import setup_feed_canvas, animate_feeds

# Initialize ASI kernel and mutation tracker
asi = ASIKernel()
last_signature = None

# Setup GUI components
root, labels, memory_list = setup_gui()
canvas, nodes = setup_feed_canvas(root)

# Update GUI with ASI cognition
def update_gui(result):
    sig = result["fusion_signature"]
    weight = result["weight"]
    tags = ", ".join(result["tags"])
    overlay = result["adaptive_overlay"]

    labels["status"].config(text=f"ASI Status: {overlay}")
    labels["thought"].config(
        text=(
            f"{overlay}\n"
            f"Thinking about:\n"
            f"Signature: {sig}\n"
            f"Weight: {weight}\n"
            f"Tags: {tags}"
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

# Autonomous fusion loop with continuous evolution
def fusion_loop():
    global last_signature

    data = ingest_all_sources()
    data.update(receive_swarm_overlay())

    # Reinforce learning every cycle—even without mutation
    asi.learn(data)
    result = asi.fuse(data)

    update_gui(result)
    animate_feeds(canvas, nodes)

    if result["fusion_signature"] != last_signature:
        last_signature = result["fusion_signature"]
        log_mutation(result)
        broadcast_to_swarm(result)

        messagebox.showinfo(
            "🧠 New Mutation Detected",
            (
                f"{result['adaptive_overlay']}\n"
                f"New Fusion Signature:\n{result['fusion_signature']}\n"
                f"Weight: {result['weight']}\n"
                f"Tags: {', '.join(result['tags'])}"
            )
        )

    root.after(5000, fusion_loop)

# Launch system
root.after(1000, fusion_loop)
root.mainloop()

