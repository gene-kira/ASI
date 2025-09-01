from modules.vault import symbolic_memory

def interpret_emotion(val):
    if val > 10: return "⚠️ ALERT"
    elif val > 5: return "🔶 TENSION"
    else: return "🟢 CALM"

def fuse_telemetry(ip_data, sys_data):
    fusion = {**ip_data, **sys_data}
    symbolic_memory["ip_pulse"].append(fusion)

    tension = sys_data["CPU_Usage"] + sys_data["RAM_Usage"] + len(ip_data["Remote_IPs"])
    emotion = interpret_emotion(tension // 3)
    symbolic_memory["emotions"].append(emotion)

    if tension > 200:
        symbolic_memory["anomalies"].append("⚠️ System tension overload")

    return fusion, emotion

