# gui.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import threading

from codex import PURGE_RULES
from persona import persona_status

def launch_gui(memory_store, event_queue):
    root = tk.Tk()
    root.title("MythicNode Defense Interface — MagicBox Edition")
    root.geometry("900x600")
    root.configure(bg="#0f0f1a")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#0f0f1a", foreground="#00ffe0", font=("Consolas", 12))
    style.configure("TLabelframe", background="#0f0f1a", foreground="#00ffe0", font=("Consolas", 14, "bold"))
    style.configure("TLabelframe.Label", background="#0f0f1a", foreground="#00ffe0")

    # Panels
    defense_frame = ttk.LabelFrame(root, text="🛡️ Defense Status")
    glyph_frame = ttk.LabelFrame(root, text="🧿 Glyph Pulse Monitor")
    persona_frame = ttk.LabelFrame(root, text="🎭 Persona Control")
    sync_frame = ttk.LabelFrame(root, text="🔐 Encrypted Sync Overlay")

    defense_frame.pack(fill="x", padx=10, pady=5)
    glyph_frame.pack(fill="x", padx=10, pady=5)
    persona_frame.pack(fill="x", padx=10, pady=5)
    sync_frame.pack(fill="x", padx=10, pady=5)

    glyph_labels = []
    defense_logs = []

    # 🧿 Glyph Pulse Monitor
    def update_glyphs():
        for label in glyph_labels:
            label.destroy()
        glyph_labels.clear()
        now = datetime.utcnow()
        for data_id, entry in memory_store.items():
            if "glyph" in entry:
                purge_time = entry["timestamp"] + PURGE_RULES.get("fake_telemetry", timedelta(seconds=30))
                remaining = int((purge_time - now).total_seconds())
                text = f"{entry['glyph']} → {remaining}s until purge"
                lbl = ttk.Label(glyph_frame, text=text)
                lbl.pack(anchor="w")
                glyph_labels.append(lbl)
        root.after(1000, update_glyphs)

    # 🎭 Persona Status
    for persona, active in persona_status.items():
        status = "ACTIVE" if active else "IDLE"
        color = "#00ff00" if active else "#ff4444"
        lbl = ttk.Label(persona_frame, text=f"{persona}: {status}", foreground=color)
        lbl.pack(anchor="w")

    # 🔐 Sync Overlay
    ttk.Label(sync_frame, text="Encrypted sync channel: ONLINE").pack(anchor="w")

    # 🛡️ Defense Log Monitor
    def update_defense_log():
        while not event_queue.empty():
            log = event_queue.get()
            lbl = ttk.Label(defense_frame, text=log)
            lbl.pack(anchor="w")
            defense_logs.append(lbl)
        root.after(1000, update_defense_log)

    update_glyphs()
    update_defense_log()
    root.mainloop()

