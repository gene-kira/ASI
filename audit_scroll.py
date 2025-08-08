from datetime import datetime

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[AuditScroll] 📜 {timestamp} — {message}")

