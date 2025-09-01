import tkinter as tk
from modules.vault import symbolic_memory
from modules.telemetry import get_ip_telemetry
from modules.system_pulse import get_system_telemetry

class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 VeilMind Nexus — Zero Trust IP Fusion")
        self.root.geometry("520x420")
        self.root.configure(bg="#1e1e2f")

        self.title = tk.Label(root, text="VeilMind Nexus", font=("Helvetica", 16, "bold"), fg="#00ffff", bg="#1e1e2f")
        self.title.pack(pady=10)

        self.labels = {}
        for label in ["Local_IP", "Public_IP", "Remote_IPs"]:
            lbl = tk.Label(root, text=f"{label}: --", font=("Helvetica", 12), fg="#ffffff", bg="#1e1e2f")
            lbl.pack(anchor="w", padx=10)
            self.labels[label] = lbl

        self.sys_labels = {}
        for label in ["CPU_Usage", "RAM_Usage", "Entropy_Pulse"]:
            lbl = tk.Label(root, text=f"{label}: --", font=("Helvetica", 12), fg="#ffaa00", bg="#1e1e2f")
            lbl.pack(anchor="w", padx=10)
            self.sys_labels[label] = lbl

        self.mutation_label = tk.Label(root, text="Mutation ID: --", font=("Helvetica", 10), fg="#ff00ff", bg="#1e1e2f")
        self.mutation_label.pack(pady=5)

        self.emotion_label = tk.Label(root, text="Last Emotion: --", font=("Helvetica", 12), fg="#00ff00", bg="#1e1e2f")
        self.emotion_label.pack(pady=5)

        self.anomaly_label = tk.Label(root, text="Anomaly: --", font=("Helvetica", 10), fg="#ff4444", bg="#1e1e2f")
        self.anomaly_label.pack(pady=5)

        self.update_loop()

    def update_loop(self):
        telemetry = get_ip_telemetry()
        sys_telemetry = get_system_telemetry()

        for key in self.labels:
            self.labels[key].config(text=f"{key}: {telemetry[key]}")

        for key in self.sys_labels:
            self.sys_labels[key].config(text=f"{key}: {sys_telemetry[key]}")

        mutation = symbolic_memory["mutations"][-1] if symbolic_memory["mutations"] else "--"
        emotion = symbolic_memory["emotions"][-1] if symbolic_memory["emotions"] else "--"
        anomaly = symbolic_memory["anomalies"][-1] if symbolic_memory["anomalies"] else "--"

        self.mutation_label.config(text=f"Mutation ID: {mutation}")
        self.emotion_label.config(text=f"Last Emotion: {emotion}")
        self.anomaly_label.config(text=f"Anomaly: {anomaly}")

        self.root.after(5000, self.update_loop)

