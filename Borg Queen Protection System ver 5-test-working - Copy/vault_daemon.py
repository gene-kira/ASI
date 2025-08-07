# vault_daemon.py
import time
import random
from zero_trust_core import ZeroTrustCore

class VaultDaemon:
    def __init__(self):
        self.vaults = {}
        self.audit_log = []
        self.ztc = ZeroTrustCore()

    def register_vault(self, name):
        glyph_key = self.ztc.generate_glyph_key(name)
        self.vaults[name] = {
            "glyph": glyph_key,
            "status": "secure",
            "last_purge": None
        }

    def assess_threat(self, name):
        return random.uniform(0, 1)

    def purge_vault(self, name):
        if name not in self.vaults:
            return False
        self.vaults[name]["status"] = "purged"
        self.vaults[name]["last_purge"] = time.time()
        self.audit_log.append(f"💣 Vault '{name}' purged at {time.ctime()}")
        return True

    def regenerate_vault(self, name):
        glyph_key = self.ztc.generate_glyph_key(name)
        self.vaults[name] = {
            "glyph": glyph_key,
            "status": "secure",
            "last_purge": None
        }
        self.audit_log.append(f"🛠️ Vault '{name}' regenerated at {time.ctime()}")

    def auto_defend(self, name):
        threat = self.assess_threat(name)
        if threat > 0.7:
            self.purge_vault(name)
            time.sleep(1.5)
            self.regenerate_vault(name)

    def get_audit_log(self):
        return self.audit_log[-10:]

