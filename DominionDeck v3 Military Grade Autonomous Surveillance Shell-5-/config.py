# 🔐 Vault path
VAULT_PATH = "ip_vault.json"

# 🛡️ Threat definitions
BLOCKED_COUNTRIES = ["RU", "CN", "IR", "KP"]
AD_DOMAINS = ["doubleclick.net", "ads.google.com", "adnxs.com", "pubmatic.com"]
TRACKERS = ["facebook.net", "google-analytics.com", "mixpanel.com", "segment.io"]
FINGERPRINTERS = ["fingerprintjs.com", "deviceinfo.io", "browserleaks.com"]

# 🧬 Persona overlays
PERSONAS = ["ShadowGlyph", "VaultWarden", "EchoMask", "AdminGlyph"]

# 📡 Log size limit
MAX_LOG_LINES = 500

# 🔮 Glyph lockdown definitions
GLYPH_LOCKDOWNS = {
    "BlackSun": [80, 443, 53],       # HTTP, HTTPS, DNS
    "IronMask": "UDP",               # Quarantine all UDP
    "EchoSeal": "VAULT_ONLY",        # Allow only whitelisted ports
    "NullGlyph": "PURGE_ALL"         # Kill all outbound streams
}

