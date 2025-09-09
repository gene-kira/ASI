# swarm.py

import requests, time, subprocess
from vault import log_feed
from asi_core import asi_decision_engine

ip_feed = {}  # {ip: {country, lat, lon}}

def geo_ip(ip):
    try:
        geo = requests.get(f"https://ipapi.co/{ip}/json").json()
        return {
            "country": geo.get("country_name", "Unknown"),
            "lat": float(geo.get("latitude", 0)),
            "lon": float(geo.get("longitude", 0))
        }
    except:
        return {"country": "Unknown", "lat": 0, "lon": 0}

def track_ip_connections():
    while True:
        try:
            ip = requests.get("https://api.ipify.org").text
            geo = geo_ip(ip)
            ip_feed[ip] = geo
            log_feed.append(f"[CONNECTED] {ip} from {geo['country']}")
        except:
            log_feed.append("[ERROR] IP tracking failed")
        time.sleep(60)

def get_local_ips():
    try:
        result = subprocess.check_output("arp -a", shell=True).decode()
        lines = result.splitlines()
        ips = [line.split()[0] for line in lines if "." in line]
        return ips
    except:
        return ["[ERROR] Failed to scan local network"]

def swarm_sync_decision():
    for ip in ip_feed:
        decision = asi_decision_engine("connection", ip, "telemetry_ping")
        log_feed.append(f"[SWARM SYNC] {ip} → {decision}")

