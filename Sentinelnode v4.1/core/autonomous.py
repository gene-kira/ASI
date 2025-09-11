import threading
import time
from core.packet import Packet

def autonomous_ingest(node):
    while True:
        packet = Packet("10.0.0.5", 4321, "ops_user", ["live", "anomaly", "ASI"], live=True)
        node.ingest(packet)
        node.destructor.enforce()
        threading.Event().wait(5)

