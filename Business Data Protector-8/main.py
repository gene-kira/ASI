# main.py

import sys, subprocess, threading, time, psutil, requests, platform
from utils import log_codex
from asi_brain import ASIBrain
from defense_daemon import (
    store_sensitive_data, purge_expired_data,
    emit_fake_telemetry, purge_telemetry,
    track_mac_ip, monitor_backdoor_data
)

def get_country_from_ip(ip):
    try:
        return requests.get(f"https://ipapi.co/{ip}/json/").json().get("country_name", "Unknown")
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
    from main_gui import MythicNodeGUI
    app = MythicNodeGUI()
    brain = ASIBrain(app.memory)
    brain.train_model([[20, 30], [50, 60], [100, 200]])
    start_daemon(app, brain)
    app.root.mainloop()

def start_daemon(app, brain):
    def loop():
        last_stats = psutil.net_io_counters(pernic=True)

        while True:
            try:
                scan_health(app)
                scan_ports(app)

                current_stats = psutil.net_io_counters(pernic=True)
                for iface in app.swarm_nodes:
                    if iface in current_stats and iface in last_stats:
                        prev, curr = last_stats[iface], current_stats[iface]
                        sent = (curr.bytes_sent - prev.bytes_sent) // 1024
                        recv = (curr.bytes_recv - prev.bytes_recv) // 1024
                        ip = app.swarm_nodes[iface].split("(")[-1].strip(")")
                        country = get_country_from_ip(ip)

                        brain.analyze_traffic(ip, country, sent, recv)
                        emit_fake_telemetry("MythicNode")
                        track_mac_ip("00:00:00:00:00", ip)
                        monitor_backdoor_data({"origin": "unauthorized"})

                        entry = store_sensitive_data("face_scan_001", "Face Scan", "Camera Module")
                        app.memory.append(entry)

                        app.traffic_monitor_panel.after(0, lambda i=iface, s=sent, r=recv: app.traffic_monitor_panel.update_traffic(i, s, r))

                last_stats = current_stats
                purge_expired_data(app.memory)
                purge_telemetry()
                brain.mutate_codex()
                brain.sync_with_swarm(app.swarm_nodes)

                app.threat_matrix_panel.after(0, lambda: app.threat_matrix_panel.log_threat("🧠 Threat matrix updated"))
                app.codex_dashboard_panel.after(0, lambda: app.codex_dashboard_panel.load_codex(brain.export_codex()))

            except Exception as e:
                log_codex(f"🔥 Daemon error: {e}")
            time.sleep(10)

    threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    launch()

