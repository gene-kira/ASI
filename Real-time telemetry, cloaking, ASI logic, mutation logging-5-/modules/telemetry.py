import psutil, socket, requests
from modules.vault import symbolic_memory

def get_ip_telemetry():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        public_ip = requests.get("https://api.ipify.org").text
        connections = psutil.net_connections(kind='inet')
        remote_ips = list(set(conn.raddr.ip for conn in connections if conn.raddr))
        return {
            "Local_IP": local_ip,
            "Public_IP": public_ip,
            "Remote_IPs": remote_ips[:5]
        }
    except Exception as e:
        symbolic_memory["anomalies"].append(f"Telemetry error: {e}")
        return {"Local_IP": "N/A", "Public_IP": "N/A", "Remote_IPs": []}

