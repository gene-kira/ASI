import tkinter as tk
from tkinter import ttk, messagebox
from config import config_path, log_path, persona_presets
from registry import reset_location
from zones import fetch_ip_map_all
from mutation import mutate
from encoding_detector import detect_encoding
import os

def launch_gui(ip_map):
    global location_var, persona_var, status_label, log_text, location_menu

    root = tk.Tk()
    root.title("DominionDeck GeoMask Console — Modular Shell")
    root.geometry("1000x700")
    root.resizable(True, True)

    ttk.Label(root, text="Select Symbolic Zone:", font=("Segoe UI", 12)).pack(pady=10)
    default_zone = next(iter(ip_map))
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8", errors="replace") as f:
                default_zone = f.read().strip()
        except:
            pass

    location_var = tk.StringVar(value=default_zone)
    location_menu = ttk.Combobox(root, textvariable=location_var, values=list(ip_map.keys()), state="readonly", font=("Segoe UI", 11))
    location_menu.pack(pady=5)

    ttk.Label(root, text="Persona Overlay:", font=("Segoe UI", 12)).pack(pady=10)
    persona_var = tk.StringVar(value=persona_presets[0])
    persona_menu = ttk.Combobox(root, textvariable=persona_var, values=persona_presets, state="readonly", font=("Segoe UI", 11))
    persona_menu.pack(pady=5)

    def trigger_mutation():
        zone = location_var.get()
        persona = persona_var.get()
        data = ip_map.get(zone)
        if not data:
            messagebox.showerror("Mutation Error", "Invalid zone selected.")
            return
        mutate(zone, persona, data, status_label, log_text)

    def refresh_zones():
        nonlocal ip_map
        ip_map = fetch_ip_map_all()
        location_menu["values"] = list(ip_map.keys())
        location_var.set(next(iter(ip_map)))
        status_label.config(text="🧬 Zones refreshed.")

    ttk.Button(root, text="Activate GeoMask Mutation", command=trigger_mutation).pack(pady=10)
    ttk.Button(root, text="🔁 Refresh Zones", command=refresh_zones).pack(pady=5)
    ttk.Button(root, text="🕊️ Normal Mode", command=lambda: reset_location()).pack(pady=5)

    status_label = ttk.Label(root, text="🧬 Status: Awaiting Mutation", font=("Segoe UI", 10), foreground="blue")
    status_label.pack(pady=5)

    ttk.Label(root, text="Mutation Vault:", font=("Segoe UI", 12)).pack(pady=10)
    log_text = tk.Text(root, height=20, wrap="word", font=("Consolas", 10))
    log_text.pack(fill="both", expand=True, padx=10)

    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as log:
                log_text.insert("end", log.read())
        except:
            with open(log_path, "rb") as f:
                raw = f.read()
                encoding = detect_encoding(raw)["encoding"]
            with open(log_path, "r", encoding=encoding, errors="replace") as log:
                log_text.insert("end", log.read())

    root.mainloop()

