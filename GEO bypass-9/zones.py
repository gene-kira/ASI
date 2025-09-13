import requests, time, json
from config import zone_cache_path

def fetch_ip_map_all():
    iso_codes = ["US","JP","DE","FR","GB","IN","BR","CA","AU","RU","CN","KR","IT","ES","MX","ZA"]
    ip_map = {}
    for iso in iso_codes:
        try:
            url = f"https://raw.githubusercontent.com/ipverse/rir-ip/master/country/{iso.lower()}/aggregated.json"
            r = requests.get(url, timeout=5)
            ip = r.json()["subnets"]["ipv4"][0].split("/")[0]
        except:
            ip = "0.0.0.0"
        ip_map[f"{iso} Zone 🌍"] = {"IP": ip, "Latitude": "0.0000", "Longitude": "0.0000"}
        time.sleep(0.3)
    with open(zone_cache_path, "w", encoding="utf-8") as f:
        json.dump(ip_map, f, indent=2)
    return ip_map

def load_ip_map():
    try:
        with open(zone_cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return fetch_ip_map_all()

