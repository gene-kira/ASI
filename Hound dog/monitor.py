import time, psutil
from voice import speak
from vault import log_threat_to_memory
from glyphs import spawn_glyph

def monitor_processes(app):
    known_connections = set()
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                conns = proc.info['connections']
                score = 0
                for conn in conns:
                    if conn.raddr and hasattr(conn.raddr, 'ip'):
                        ip = conn.raddr.ip
                        key = f"{name}-{pid}-{ip}"
                        if key not in known_connections:
                            known_connections.add(key)
                            score += 1
                            msg = f"⚠️ {name} (PID {pid}) connected to {ip}\n"
                            app.process_output.insert("end", msg)
                            app.ip_output.insert("end", msg)
                            app.threat_output.insert("end", f"🔥 Threat logged: {msg}")
                            app.mutation_output.insert("end", f"🧬 Mutation: {name} reached {ip}\n")
                            speak(f"Suspicious connection detected from {name} to {ip}.")
                            log_threat_to_memory({"name": name, "pid": pid, "ip": ip, "timestamp": time.time()})
                            spawn_glyph(app.glyphs)
                if score >= app.trust_threshold:
                    app.predictive_cloak(pid, name)
                    time.sleep(2)
                    app.terminate_process(pid, name)
            except Exception as e:
                print(f"[Monitor Error] {e}")
        time.sleep(5)

