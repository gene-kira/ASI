# main.py

import threading
import time
import psutil
import sys

from main_gui import MythicNodeGUI
from utils import log_codex
from persona_engine import inject_persona
from deception_engine import generate_decoy_ports, simulate_swarm_echo, inject_codex_mutation

sys.stdout.reconfigure(encoding='utf-8')

def launch():
    app = MythicNodeGUI()
    start_daemon(app)
    app.mainloop()

def start_daemon(app):
    def daemon_loop():
        log_codex("🧠 Daemon loop started")
        last_stats = psutil.net_io_counters(pernic=True)

        while True:
            try:
                scan_health(app)
                scan_ports(app)

                # Persona injection
                persona = inject_persona(app.memory)
                app.persona_panel.after(0, lambda: app.persona_panel.set_persona(persona))

                # Real-time sync updates
                current_stats = psutil.net_io_counters(pernic=True)
                for iface in app.swarm_nodes:
                    if iface in current_stats and iface in last_stats:
                        prev = last_stats[iface]
                        curr = current_stats[iface]
                        sent = (curr.bytes_sent - prev.bytes_sent) // 1024
                        recv = (curr.bytes_recv - prev.bytes_recv) // 1024
                        status = f"↑ {sent}KB/s | ↓ {recv}KB/s"
                        app.swarm_panel.update_sync(iface, status)
                        log_codex(f"🔄 {iface} → {status}")
                    else:
                        log_codex(f"⚠️ Interface missing in stats: {iface}")
                last_stats = current_stats

                # Matrix + dashboard
                app.threat_matrix_panel.after(0, app.threat_matrix_panel.update_matrix)
                app.codex_dashboard_panel.after(0, app.codex_dashboard_panel.load_codex)

                # Deception pulses
                generate_decoy_ports()
                simulate_swarm_echo()
                inject_codex_mutation()

                app.status_panel.update_enhancer("Idle")
                log_codex("🌀 MythicNode heartbeat: system secure")
            except Exception as e:
                log_codex(f"🔥 Daemon error: {e}")
            time.sleep(1)

    threading.Thread(target=daemon_loop, daemon=True).start()

def scan_health(app):
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        if "personal_data_protector" in proc.info['name'].lower():
            mem = proc.info['memory_info'].rss / (1024 * 1024)
            status = f"OK ({mem:.2f}MB)"
            emergency = "Memory overload" if mem > 500 else None
            app.status_panel.update_health(status, emergency)
            found = True
            break
    if not found:
        app.status_panel.update_health("❌ Not running", "PDP offline")

def scan_ports(app):
    ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            ports.append(conn.laddr.port)
    app.status_panel.update_ports(ports)

if __name__ == "__main__":
    launch()

