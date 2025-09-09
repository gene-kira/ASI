# vault.py

import time
from config import ZERO_TRUST_DOMAINS, DEST_WHITELIST
data_vault = {}
log_feed = []

def validate_destination(destination):
    return destination in DEST_WHITELIST

def send_data_securely(key, value, destination):
    if validate_destination(destination):
        log_feed.append(f"[DATA SENT] {key} → {destination}")
    else:
        log_feed.append(f"[DATA PURGED] {key} → {destination} rejected")
        data_vault.pop(key, None)

def ingest_data(key, value, ttl, source="internal"):
    if source in ZERO_TRUST_DOMAINS:
        log_feed.append(f"[BLOCKED] {key} from {source}")
        return
    data_vault[key] = {"value": value, "timestamp": time.time(), "ttl": ttl}
    log_feed.append(f"[INGESTED] {key} | TTL={ttl}s")

def monitor_data():
    while True:
        now = time.time()
        for key in list(data_vault.keys()):
            if now - data_vault[key]["timestamp"] >= data_vault[key]["ttl"]:
                log_feed.append(f"[PURGED] {key}")
                del data_vault[key]
        time.sleep(1)

