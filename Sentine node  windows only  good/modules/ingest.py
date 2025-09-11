# ingest.py
import socket, time, struct, ctypes, sys, os
from modules.sanitizer import DataSanitizer

class RealTimeIngest:
    def __init__(self):
        self.buffer = []
        self.sock = None
        self.sanitizer = DataSanitizer()

    def require_admin(self):
        if os.name == 'nt':
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            except:
                is_admin = False
            if not is_admin:
                params = ' '.join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                sys.exit()

    def activate_live_stream(self):
        self.require_admin()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        self.sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def get_live_state(self):
        raw_data, addr = self.sock.recvfrom(65535)
        packet = self._parse_ip_packet(raw_data)
        self.sanitizer.tag_mac_ip(packet["src_ip"])
        self.sanitizer.tag_mac_ip(packet["dst_ip"])
        self.sanitizer.tag_fake_telemetry({"cpu": 99.9, "temp": 999})
        self.sanitizer.purge_expired()
        return packet

    def _parse_ip_packet(self, raw_data):
        try:
            ip_header = raw_data[:20]
            iph = struct.unpack("!BBHHHBBH4s4s", ip_header)
            src_ip = socket.inet_ntoa(iph[8])
            dst_ip = socket.inet_ntoa(iph[9])
            protocol = iph[6]
            payload = raw_data[20:]
            return {
                "timestamp": time.time(),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "payload": payload
            }
        except:
            return {
                "timestamp": time.time(),
                "src_ip": "0.0.0.0",
                "dst_ip": "0.0.0.0",
                "protocol": 0,
                "payload": b""
            }

