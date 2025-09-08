# main.py

import sys, subprocess, threading, time, psutil, requests, platform
from main_gui import MythicNodeGUI
from utils import log_codex
from persona_engine import inject_persona
from deception_engine import trigger_deception_overlay
from ip_blocker import block_ip_temporary, unblock_ip
from defense_daemon import emit_fake_telemetry, store_sensitive_data
from asi_brain import ASIBrain

# Auto-install required libraries
required_libs = ["tkinter", "psutil", "requests", "hidpi-tk", "sklearn", "numpy"]
for lib in required_libs:
    try: __import__(lib)
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Geo-block list
blocked_countries = {"Russia": True, "China": True, "North Korea": True, "Iran": True}

def get_country_from_ip(ip):
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/")
        return res.json().get("country_name", "Unknown")
    except:
        return "Unknown"

def scan_health(app):
    for proc in psutil.process_iter(['name', 'memory_info']):
        if "personal_data_protector" in proc.info['name'].lower():
            mem = proc.info['memory_info'].rss / (1024 * 1024)
            status = f"OK ({mem:.2f}MB)"
            emergency = "Memory overload" if mem > 500 else None
            app.status_panel.after(0, lambda: app.status_panel.update_health(status, emergency))
            return
    app.status_panel.after(0, lambda: app.status_panel.update_health("❌ Not running", "PDP offline"))

def scan_ports(app):
    ports = [conn.laddr.port for conn in psutil.net_connections(kind='inet') if conn.status == 'LISTEN']
    app.status_panel.after(0, lambda: app.status_panel.update_ports(ports))

def launch():
    app = MythicNodeGUI()
    brain = ASIBrain(app.memory)
    brain.train_model([[20, 30], [50, 60], [100, 200], [10, 15]])  # Sample traffic training
    start_daemon(app, brain)
    app.mainloop()

def start_daemon(app, brain):
    def daemon_loop():
        log_codex("🧠 Daemon loop started")
        last_stats = psutil.net_io_counters(pernic=True)

        while True:
            try:
                scan_health(app)
                scan_ports(app)

                persona = inject_persona(app.memory)
                app.persona_panel.after(0, lambda: app.persona_panel.set_persona(persona))

                current_stats = psutil.net_io_counters(pernic=True)
                for iface in app.swarm_nodes:
                    if iface in current_stats and iface in last_stats:
                        prev = last_stats[iface]
                        curr = current_stats[iface]
                        sent = (curr.bytes_sent - prev.bytes_sent) // 1024
                        recv = (curr.bytes_recv - prev.bytes_recv) // 1024

                        ip = app.swarm_nodes[iface].split("(")[-1].strip(")")
                        country = get_country_from_ip(ip)

                        # 🔥 ASI Brain analysis
                        brain.analyze_traffic(ip, country, sent, recv)

                        # GUI updates
                        app.swarm_panel.after(0, lambda i=iface, s=f"↑ {sent}KB/s | ↓ {recv}KB/s": app.swarm_panel.update_sync(i, s))
                        app.traffic_monitor_panel.after(0, lambda i=iface, s=sent, r=recv: app.traffic_monitor_panel.update_traffic(i, s, r))

                last_stats = current_stats

                emit_fake_telemetry("MythicNode")
                store_sensitive_data("face_scan_001", "Face Scan", "Camera Module")

                brain.mutate_codex()
                brain.sync_with_swarm(app.swarm_nodes)

                app.threat_matrix_panel.after(0, lambda: app.threat_matrix_panel.log_threat("🧠 Threat matrix refreshed"))
                app.codex_dashboard_panel.after(0, lambda: app.codex_dashboard_panel.load_codex(brain.export_codex()))
                app.status_panel.after(0, lambda: app.status_panel.update_enhancer("Idle"))

            except Exception as e:
                log_codex(f"🔥 Daemon error: {e}")
            time.sleep(10)

    threading.Thread(target=daemon_loop, daemon=True).start()

if __name__ == "__main__":
    launch()

