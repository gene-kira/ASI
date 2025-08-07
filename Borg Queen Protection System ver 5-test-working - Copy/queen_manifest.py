# queen_manifest.py
import time

class Manifest:
    def __init__(self):
        self.modules = {}
        self.assets = {}
        self.audit_log = []

    def register_module(self, name, path, version="1.0"):
        self.modules[name] = {
            "path": path,
            "version": version,
            "registered_at": time.time()
        }
        self.audit_log.append(f"glyph(manifest:module:{name})")

    def register_asset(self, name, location, type="data"):
        self.assets[name] = {
            "location": location,
            "type": type,
            "registered_at": time.time()
        }
        self.audit_log.append(f"glyph(manifest:asset:{name})")

    def get_manifest(self):
        return {
            "modules": self.modules,
            "assets": self.assets
        }

    def get_audit_log(self):
        return self.audit_log[-5:]

