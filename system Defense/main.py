# main.py

from autoloader import ensure_dependencies
from daemon import ingest, daemon_loop

# 🔄 Ensure all required libraries are installed
ensure_dependencies()

# 🧠 Sample Threat Ingests
ingest("mac:00:1A:2B:3C:4D:5E ip:192.168.1.1", origin="RU")
ingest("backdoor leak detected", origin="RU")
ingest("fake telemetry stream", origin="RU")
ingest("face recognition data, phone:555-1234", origin="RU")
ingest("driver license: X1234567", origin="RU")

# 🛡️ Launch MythicNode Daemon
daemon_loop()

