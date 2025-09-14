import requests
from config import BLOCKED_COUNTRIES, AD_DOMAINS, TRACKERS, FINGERPRINTERS
from vault import load_vault

def check_outbound_risk():
    try:
        ip = requests.get("https://api.ipify.org").text
        geo = requests.get(f"https://ipapi.co/{ip}/country/").text
        return ip, geo
    except Exception as e:
        print(f"GeoTrace error: {e}")
        return "0.0.0.0", "??"

def scan_payload_for_risks(ip, domain):
    vault = load_vault()
    if ip in vault["block"] or domain in AD_DOMAINS + TRACKERS + FINGERPRINTERS:
        return "block"
    if ip in vault["allow"]:
        return "allow"
    for risk in AD_DOMAINS + TRACKERS + FINGERPRINTERS:
        if risk in domain:
            return "block"
    return "unknown"

