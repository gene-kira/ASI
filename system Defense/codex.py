from datetime import timedelta

PURGE_RULES = {
    "mac_ip": timedelta(seconds=30),
    "mac_ip_extended": timedelta(days=1),
    "backdoor_leak": timedelta(seconds=3),
    "personal_data": timedelta(days=1),
    "fake_telemetry": timedelta(seconds=30)
}

ZERO_TRUST_DOMAINS = ["AI", "ASI", "hacker"]
PERSONAL_KEYS = ["face", "finger", "bio", "phone", "address", "license", "social"]

def classify(data):
    tags = []
    if any(k in data for k in PERSONAL_KEYS):
        tags.append("personal_data")
    if "mac" in data or "ip" in data:
        tags.append("mac_ip")
    if "telemetry" in data and "fake" in data:
        tags.append("fake_telemetry")
    if "backdoor" in data:
        tags.append("backdoor_leak")
    return tags

