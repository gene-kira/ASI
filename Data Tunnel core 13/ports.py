import psutil
import socket
from datetime import datetime
from codex import log_event

TCP_COLOR = "#ffcc00"
UDP_COLOR = "#3399ff"
TEXT_COLOR = "#c5c6c7"

def scan_active_ports(canvas):
    """
    Scans active TCP/UDP ports and draws rings for each.
    Logs port activity to the codex.
    """
    connections = psutil.net_connections()
    for conn in connections:
        if conn.status == "ESTABLISHED" and conn.laddr:
            port = conn.laddr.port
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            color = TCP_COLOR if proto == "TCP" else UDP_COLOR
            label = f"{proto} Port {port}"

            x = 20 + (port % 360)
            ring = canvas.create_oval(
                x, 20, x + 40, 60,
                outline=color, width=2
            )
            text = canvas.create_text(
                x + 20, 70,
                text=label, fill=TEXT_COLOR, font=("Helvetica", 6)
            )
            canvas.after(1000, lambda r=ring, t=text: canvas.delete(r) or canvas.delete(t))

            entry = {
                "event": "port_data_detected",
                "port": port,
                "protocol": proto,
                "status": conn.status,
                "timestamp": datetime.now().isoformat()
            }
            log_event(entry)
            print(f"[📡] Active {proto} port detected: {port}")

