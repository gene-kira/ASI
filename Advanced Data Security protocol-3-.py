import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# 🔐 Configuration
AUTHORIZED_DESTINATIONS = {"192.168.1.100", "10.0.0.42"}
SELF_DESTRUCT_DELAY = {
    "backdoor": 3,
    "no_mac_ip": 30,
    "mac_ip": 86400,
    "personal_data": 86400,
    "fake_telemetry": 30
}

# 🧬 ASI-Controlled Sentinel Core
class ASISentinel:
    def __init__(self, gui_callback):
        self.memory = {}
        self.mutation_log = []
        self.symbolic_feedback = []
        self.gui_callback = gui_callback

    def intercept_packet(self, packet):
        packet_id = packet["id"]
        self.memory[packet_id] = {
            "timestamp": datetime.now(),
            "metadata": packet,
            "mutation_lineage": [],
            "status": "intercepted"
        }
        self.evaluate_packet(packet_id)

    def evaluate_packet(self, packet_id):
        packet = self.memory[packet_id]["metadata"]
        reasons = []

        # Zero Trust Enforcement
        if not packet.get("auth") or packet.get("destination") not in AUTHORIZED_DESTINATIONS:
            reasons.append("Unauthorized destination/token")
            self.schedule_purge(packet_id, SELF_DESTRUCT_DELAY["backdoor"], reasons[-1])

        # MAC/IP Validation
        if not packet.get("mac") or not packet.get("ip"):
            reasons.append("Missing MAC/IP")
            self.schedule_purge(packet_id, SELF_DESTRUCT_DELAY["no_mac_ip"], reasons[-1])
        else:
            self.schedule_purge(packet_id, SELF_DESTRUCT_DELAY["mac_ip"], "MAC/IP expiration")

        # Personal Data TTL
        if packet.get("type") == "personal":
            reasons.append("Personal data TTL")
            self.schedule_purge(packet_id, SELF_DESTRUCT_DELAY["personal_data"], reasons[-1])

        self.log_mutation(packet_id, reasons)

    def schedule_purge(self, packet_id, delay, reason):
        def purge():
            time.sleep(delay)
            self.memory[packet_id]["status"] = "purged"
            self.symbolic_feedback.append(f"{packet_id} purged due to: {reason}")
            self.gui_callback(packet_id, reason)
        threading.Thread(target=purge, daemon=True).start()

    def log_mutation(self, packet_id, reasons):
        lineage = {
            "packet_id": packet_id,
            "timestamp": datetime.now(),
            "reasons": reasons
        }
        self.mutation_log.append(lineage)
        self.memory[packet_id]["mutation_lineage"].append(lineage)

    def deploy_fake_telemetry(self):
        data_id = f"telemetry_{int(time.time())}"
        packet = {
            "id": data_id,
            "timestamp": datetime.now(),
            "type": "telemetry",
            "auth": None,
            "destination": None,
            "mac": None,
            "ip": None
        }
        self.memory[data_id] = {
            "timestamp": datetime.now(),
            "metadata": packet,
            "mutation_lineage": [],
            "status": "deployed"
        }
        self.schedule_purge(data_id, SELF_DESTRUCT_DELAY["fake_telemetry"], "Fake telemetry purge")
        self.gui_callback(data_id, "Fake telemetry deployed")

# 🖥️ Passive GUI Interface (No buttons, just symbolic feedback)
class SentinelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Borg Sentinel Control Shell")
        self.tree = ttk.Treeview(root, columns=("Reason", "Status"), show="headings")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Initialize ASI Sentinel
        self.sentinel = ASISentinel(self.update_status)

        # Start autonomous loop
        threading.Thread(target=self.autonomous_loop, daemon=True).start()

    def update_status(self, data_id, reason):
        self.tree.insert("", "end", values=(reason, f"{data_id} PURGED"))

    def autonomous_loop(self):
        while True:
            self.sentinel.deploy_fake_telemetry()
            time.sleep(60)  # Adjust frequency as needed

# 🧱 Launch
if __name__ == "__main__":
    root = tk.Tk()
    gui = SentinelGUI(root)
    root.mainloop()

