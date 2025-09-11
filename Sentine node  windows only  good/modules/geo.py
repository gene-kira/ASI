# geo.py
import requests
from modules.sanitizer import DataSanitizer

class IPGeoLocator:
    def __init__(self, token):
        self.token = token
        self.endpoint = "https://ipinfo.io"
        self.sanitizer = DataSanitizer()

    def lookup(self, ip):
        if not ip or ip == "0.0.0.0":
            return {"ip": ip, "error": "Invalid IP"}
        try:
            response = requests.get(f"{self.endpoint}/{ip}", params={"token": self.token}, timeout=5)
            data = response.json()
            loc = data.get("loc", "0,0").split(",")
            geo_data = {
                "ip": ip,
                "city": data.get("city", "Unknown"),
                "region": data.get("region", ""),
                "country": data.get("country", ""),
                "latitude": loc[0],
                "longitude": loc[1],
                "org": data.get("org", "Unknown")
            }
            self.sanitizer.tag_personal_data(geo_data)
            self.sanitizer.purge_expired()
            return geo_data
        except:
            return {"ip": ip, "error": "Geo lookup failed"}

