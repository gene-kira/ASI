import socket, uuid, psutil
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.mac = self.get_mac()

    def get_mac(self):
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    return addr.address
        return "00:00:00:00:00:00"

    def snapshot(self):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": self.hostname,
            "ip": self.ip,
            "mac": self.mac,
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent,
            "uuid": str(uuid.uuid4())
        }

