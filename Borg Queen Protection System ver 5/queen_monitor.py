# queen_monitor.py
import psutil
import socket

class Monitor:
    def __init__(self, cpu_threshold=85, mem_threshold=85):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold

    def check_cpu_memory(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        return {
            "cpu": cpu,
            "memory": mem,
            "anomaly": cpu > self.cpu_threshold or mem > self.mem_threshold
        }

    def list_suspicious_processes(self):
        suspicious = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 50 or proc.info['memory_percent'] > 10:
                    suspicious.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return suspicious

    def list_open_ports(self):
        connections = psutil.net_connections(kind='inet')
        open_ports = []
        for conn in connections:
            if conn.status == 'LISTEN':
                open_ports.append({
                    "pid": conn.pid,
                    "port": conn.laddr.port,
                    "ip": conn.laddr.ip
                })
        return open_ports

    def list_remote_connections(self):
        connections = psutil.net_connections(kind='inet')
        remote = []
        for conn in connections:
            if conn.raddr and conn.status == 'ESTABLISHED':
                remote.append({
                    "pid": conn.pid,
                    "remote_ip": conn.raddr.ip,
                    "remote_port": conn.raddr.port
                })
        return remote

    def scan(self):
        return {
            "cpu_mem": self.check_cpu_memory(),
            "suspicious_processes": self.list_suspicious_processes(),
            "open_ports": self.list_open_ports(),
            "remote_connections": self.list_remote_connections()
        }

