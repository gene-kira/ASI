import hashlib, datetime
from registry import set_registry
from config import config_path, log_path

def mutate(zone, persona, data, status_label, log_text):
    set_registry(r"Software\\Microsoft\\Windows\\CurrentVersion\\Location", "Latitude", data["Latitude"])
    set_registry(r"Software\\Microsoft\\Windows\\CurrentVersion\\Location", "Longitude", data["Longitude"])
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ancestry = hashlib.sha256((zone + timestamp).encode()).hexdigest()[:12]
    log_entry = f"{timestamp} — [{persona}] → {zone} via IP {data['IP']} ({data['Latitude']}, {data['Longitude']}) [#{ancestry}]"
    with open(log_path, "a", encoding="utf-8", errors="replace") as log:
        log.write(log_entry + "\n")
    with open(config_path, "w", encoding="utf-8", errors="replace") as cfg:
        cfg.write(zone)
    status_label.config(text=f"🧬 Mutation Complete: {zone} ({data['IP']})")
    log_text.insert("end", log_entry + "\n")
    log_text.see("end")

