# discovery.py
import socket
import threading
import time

DISCOVERY_PORT = 9999
NODE_ID = socket.gethostname()

def broadcast_presence():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = f"MagicBox:{NODE_ID}".encode()
    def loop():
        while True:
            sock.sendto(message, ('<broadcast>', DISCOVERY_PORT))
            time.sleep(10)
    threading.Thread(target=loop, daemon=True).start()

def listen_for_nodes(callback):
    def listener():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', DISCOVERY_PORT))
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("MagicBox:"):
                node_name = msg.split(":")[1]
                timestamp = time.strftime("%H:%M:%S")
                callback(f"{node_name} @ {addr[0]} [{timestamp}]")
    threading.Thread(target=listener, daemon=True).start()

