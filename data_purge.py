from threading import Timer
from audit_scroll import log_event

def purge_data(data):
    log_event(f"Data purged: {data['id']}")
    print(f"[DataPurge] 💥 Purged: {data['id']}")

def set_timer(data, seconds, callback):
    Timer(seconds, callback, [data]).start()

def schedule_data_destruction(data):
    if data.get("type") == "personal":
        set_timer(data, 86400, purge_data)  # 1 day
    elif data.get("channel") == "backdoor":
        set_timer(data, 3, purge_data)

