# mutation_shell_mitm.py
import sys, subprocess, hashlib, time, json, os, threading

# 🔧 Autoloader
required = ["PyQt5", "requests", "beautifulsoup4", "python-whois", "mitmproxy"]
for lib in required:
    try: __import__(lib.replace("-", "_"))
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

from mitmproxy import http
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt
import requests
from bs4 import BeautifulSoup
import whois

# 🛡️ DNS Cloak Launcher (optional)
def launch_dns_cloak():
    if os.path.exists("dnsproxy.exe") and os.path.exists("telemetry_blocklist.txt"):
        subprocess.Popen([
            "dnsproxy.exe",
            "--listen", "127.0.0.1:53",
            "--upstream", "https://dns.google/dns-query",
            "--blocking-ttl", "3600",
            "--blocked-respond-nxdomain",
            "--custom-blocklist", "telemetry_blocklist.txt"
        ], creationflags=subprocess.CREATE_NO_WINDOW)

# 🧬 Symbolic ID Generator
def generate_glyph(domain, protocol):
    raw = f"{domain}-{protocol}-{time.time()}"
    h = hashlib.sha256(raw.encode()).hexdigest()
    return f"glyph://{domain}/{protocol}/{h[:6]}"

# 🌐 Website Validator
def validate_website(domain):
    result = {
        "domain": domain,
        "valid_ssl": False,
        "telemetry_detected": False,
        "fingerprinting_scripts": [],
        "country_origin": "Unknown",
        "reputation_score": 50,
        "glyph_id": generate_glyph(domain, "https"),
        "status": "yellow"
    }
    try:
        r = requests.get(f"https://{domain}", timeout=5)
        result["valid_ssl"] = True
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all("script")
        for s in scripts:
            if "canvas" in str(s) or "audioContext" in str(s):
                result["fingerprinting_scripts"].append("canvas/audioContext")
        if any(x in domain for x in ["ads", "track", "telemetry"]):
            result["telemetry_detected"] = True
        result["reputation_score"] = 90 if not result["telemetry_detected"] else 40
    except: result["status"] = "red"
    try:
        w = whois.whois(domain)
        result["country_origin"] = w.get("country", "Unknown")
    except: pass
    if result["valid_ssl"] and not result["telemetry_detected"]:
        result["status"] = "green"
    elif result["telemetry_detected"] or result["fingerprinting_scripts"]:
        result["status"] = "yellow"
    else:
        result["status"] = "red"
    return result

# 📜 Forensic Logger
def log_event(event):
    with open("mutation_log.json", "a") as f:
        f.write(json.dumps(event) + "\n")

# 🧿 GUI Shell
class MutationGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mutation Shell")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.status_light = QLabel("🟡 Awaiting traffic...")
        self.status_light.setAlignment(Qt.AlignCenter)
        self.status_light.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.status_light)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.setLayout(layout)

    def display_event(self, event):
        color = {
            "green": "background-color: #d4fcd4;",
            "yellow": "background-color: #fff9c4;",
            "red": "background-color: #f8d7da;"
        }[event["status"]]
        self.status_light.setText({
            "green": "🟢 Secure",
            "yellow": "🟡 Suspicious",
            "red": "🔴 Hostile"
        }[event["status"]])
        self.setStyleSheet(color)
        text = f"""
🔹 Glyph ID: {event['glyph_id']}
🌐 Domain: {event['domain']}
🛡️ SSL Valid: {event['valid_ssl']}
🕵️‍♂️ Fingerprinting: {event['fingerprinting_scripts']}
📍 Country: {event['country_origin']}
⚠️ Telemetry: {event['telemetry_detected']}
📊 Reputation: {event['reputation_score']}
"""
        self.output.append(text)
        log_event(event)

gui = MutationGUI()

# 🔄 mitmproxy Hook
def request(flow: http.HTTPFlow) -> None:
    domain = flow.request.host
    event = validate_website(domain)
    gui.display_event(event)

# 🚀 Launch GUI + DNS Cloak
def start_gui():
    launch_dns_cloak()
    app = QApplication([])
    gui.show()
    app.exec_()

threading.Thread(target=start_gui, daemon=True).start()
