import psutil, random
from modules.vault import symbolic_memory

def get_system_telemetry():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        entropy = random.randint(0, 100)
        return {
            "CPU_Usage": cpu,
            "RAM_Usage": ram,
            "Entropy_Pulse": entropy
        }
    except Exception as e:
        symbolic_memory["anomalies"].append(f"System telemetry error: {e}")
        return {"CPU_Usage": 0, "RAM_Usage": 0, "Entropy_Pulse": 0}

