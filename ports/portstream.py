# portstream.py

# ✅ Auto-install psutil if missing
try:
    import psutil
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

import socket
from pulse import DataPulse

def get_active_ports():
    """
    Returns a list of active ports with process metadata and protocol type.
    Each entry includes: port, pid, name, exe, proto (TCP/UDP).
    """
    connections = psutil.net_connections(kind='inet')
    ports = []
    for conn in connections:
        if conn.status == 'ESTABLISHED' and conn.laddr:
            proc = None
            try:
                proc = psutil.Process(conn.pid) if conn.pid else None
            except Exception:
                pass
            ports.append({
                "port": conn.laddr.port,
                "pid": conn.pid,
                "name": proc.name() if proc else "unknown",
                "exe": proc.exe() if proc else "unknown",
                "proto": "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            })
    return ports

def generate_port_pulses():
    """
    Generates DataPulse objects from each active port.
    Payload includes port number, process name, and protocol.
    """
    pulses = []
    for entry in get_active_ports():
        payload_str = f"{entry['proto']}:{entry['port']}:{entry['name']}"
        payload = payload_str.encode("utf-8")
        source_id = f"port_{entry['port']}_{entry['proto']}"
        pulse = DataPulse(source=source_id, payload=payload)
        pulse.process_name = entry['name']
        pulse.protocol = entry['proto']
        pulse.pid = entry['pid']
        pulse.exe = entry['exe']
        pulses.append(pulse)
    return pulses

def fuse_ports_by_process(port_data):
    """
    Groups ports by process name for symbolic fusion into daemon nodes.
    Returns a dict: {process_name: [port_entry, ...]}
    """
    fusion_map = {}
    for entry in port_data:
        key = entry["name"]
        if key not in fusion_map:
            fusion_map[key] = []
        fusion_map[key].append(entry)
    return fusion_map

