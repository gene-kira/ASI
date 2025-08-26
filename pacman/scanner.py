# scanner.py
import psutil

def live_data_scan():
    memory = []

    # 🔍 Active files from running processes
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            info = proc.info
            if info['open_files']:
                for f in info['open_files']:
                    path = f.path
                    novelty = hash(path) % 100
                    weight = (novelty + proc.pid) % 100
                    memory.append({
                        "type": "live_file",
                        "process": info['name'],
                        "path": path,
                        "novelty": novelty,
                        "weight": weight
                    })
        except Exception:
            continue

    # 🔌 Live network ports
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED':
            port = conn.laddr.port
            novelty = (port * 7) % 100
            weight = (novelty + port) % 100
            memory.append({
                "type": "live_port",
                "port": port,
                "status": conn.status,
                "novelty": novelty,
                "weight": weight
            })

    return memory

