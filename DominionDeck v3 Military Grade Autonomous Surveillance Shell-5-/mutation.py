import datetime

mutation_log = []

def narrate_event(source, action, status, persona):
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "source": source,
        "action": action,
        "status": status,
        "persona": persona,
        "timestamp": timestamp
    }
    mutation_log.append(entry)
    print(f"[{timestamp}] [{persona}] {action.upper()} → {source} [{status}]")
    return f"[{timestamp}] [{persona}] {action.upper()} → {source} [{status}]"
