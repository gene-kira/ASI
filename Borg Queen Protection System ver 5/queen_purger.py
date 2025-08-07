# queen_purger.py
import time, random

class VaultPurger:
    def __init__(self):
        self.vault = {}  # key_id: (data, expiry)
        self.audit_log = []
        self.purge_fx = []

    def add_to_vault(self, key_id, data, ttl=20):
        expiry = time.time() + ttl
        self.vault[key_id] = (data, expiry)
        self.audit_log.append(f"glyph(vault:add:{key_id})")

    def check_and_purge(self):
        now = time.time()
        purged = []
        for key_id, (data, expiry) in list(self.vault.items()):
            if expiry <= now:
                del self.vault[key_id]
                fx = self.trigger_particle_fx(key_id)
                self.purge_fx.append(fx)
                self.audit_log.append(f"glyph(purge:{key_id})")
                purged.append(key_id)
        return purged

    def trigger_particle_fx(self, key_id):
        fx = {
            "id": key_id,
            "burst": random.choice(["nova", "pulse", "shatter", "flare"]),
            "color": random.choice(["orange", "blue", "white", "magenta"]),
            "intensity": random.randint(10, 30),
            "timestamp": time.time()
        }
        return fx

    def get_recent_fx(self):
        return self.purge_fx[-5:]

    def get_audit_log(self):
        return self.audit_log[-5:]

