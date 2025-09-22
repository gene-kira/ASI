import json, os

SIGNATURE_FILE = ".ad_signatures.json"

def load_signatures():
    if os.path.exists(SIGNATURE_FILE):
        with open(SIGNATURE_FILE, "r") as f: return json.load(f)
    return []

def save_signatures(sigs):
    with open(SIGNATURE_FILE, "w") as f: json.dump(sigs, f, indent=2)

def track_signature(driver):
    try:
        elements = driver.execute_script("""
            return Array.from(document.querySelectorAll('[id*="ad"], [class*="ad"], iframe[src*="ads"]'))
                .map(e => ({tag: e.tagName, id: e.id, class: e.className}));
        """)
        return elements
    except:
        return []

