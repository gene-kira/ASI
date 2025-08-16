import socket
import struct
from core.mutation import MutationHooks

class PacketSniffer:
    def __init__(self, iface=None, mutation_hook=None):
        self.iface = iface
        self.mutator = mutation_hook or MutationHooks()

    def start_sniffing(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            sock.bind((self.iface or socket.gethostbyname(socket.gethostname()), 0))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

            self.mutator.log_mutation("Packet sniffer started (raw socket)")
            while True:
                packet, _ = sock.recvfrom(65565)
                self.process_packet(packet)

        except Exception as e:
            self.mutator.log_mutation(f"Sniffer error: {e}")

    def process_packet(self, packet):
        ip_header = packet[0:20]
        iph = struct.unpack("!BBHHHBBH4s4s", ip_header)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        protocol = iph[6]
        src_ip = socket.inet_ntoa(iph[8])
        dst_ip = socket.inet_ntoa(iph[9])

        if protocol == 6:  # TCP
            self.mutator.log_mutation(f"TCP packet: {src_ip} → {dst_ip}")
        elif protocol == 17:  # UDP
            self.mutator.log_mutation(f"UDP packet: {src_ip} → {dst_ip}")
        else:
            self.mutator.log_mutation(f"Other IP packet: {src_ip} → {dst_ip}")

