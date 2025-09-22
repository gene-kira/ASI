import socket, struct

DEFAULT_AD_DOMAINS = [b"doubleclick", b"googlesyndication", b"adnxs", b"ads", b"track", b"banner"]

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def start_sniff():
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    sock.bind((get_ip(), 0))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    return sock

def classify(proto, length, payload, whitelist):
    p = payload.lower()
    if any(d in p for d in DEFAULT_AD_DOMAINS) and not any(w.encode() in p for w in whitelist):
        return "Ad", "black"
    if b"video" in p: return "Video", "green"
    if b"json" in p or b"text" in p: return "Data", "blue"
    return "Other", "orange"

def dissect_packet(data, whitelist):
    if len(data) < 20: return None
    ip = struct.unpack('!BBHHHBBH4s4s', data[:20])
    proto = ip[6]
    src = socket.inet_ntoa(ip[8])
    dst = socket.inet_ntoa(ip[9])
    payload = data[20:100]
    label, color = classify(proto, len(data), payload, whitelist)
    ent = len(data)/1500 + (1 - {6:0.9,17:0.7}.get(proto, 0.3))
    msg = f"{src} → {dst} | {label} | Entropy: {round(ent,2)}"
    return msg, color, ent, label

