ZERO_TRUST_DOMAINS = ["AI", "ASI", "external_hacker"]
PERSONAL_DATA_KEYS = ["face", "fingerprint", "bio", "phone", "address", "license", "SSN"]
TELEMETRY_FAKE = {"cpu": "∞", "ram": "∞", "temp": "0K", "ping": "0ms"}

TIMERS = {
    "personal_data": 86400,
    "telemetry_fake": 30,
    "mac_ip_fast": 30,
    "backdoor_leak": 3
}

DEST_WHITELIST = ["192.168.1.100", "api.mytrustedserver.com", "10.0.0.5"]

