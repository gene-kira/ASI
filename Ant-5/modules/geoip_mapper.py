import geoip2.database
from core.mutation import MutationHooks

class GeoIPMapper:
    def __init__(self, db_path="GeoLite2-City.mmdb", mutation_hook=None):
        self.reader = geoip2.database.Reader(db_path)
        self.mutator = mutation_hook or MutationHooks()

    def map_ip(self, ip):
        try:
            response = self.reader.city(ip)
            location = f"{response.city.name}, {response.country.name}"
            self.mutator.log_mutation(f"GeoIP: {ip} → {location}")
            return location
        except:
            return "Unknown"

