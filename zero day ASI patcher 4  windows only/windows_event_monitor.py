import win32evtlog
import win32con
import win32event
import win32security
import time
import re

SECURITY_LOG = "Security"
EVENT_ID = 4688  # Process creation

def parse_event(record):
    data = record.StringInserts
    if not data or len(data) < 6:
        return None
    return {
        "pid": int(re.search(r"\d+", data[4]).group()),  # New Process ID
        "comm": data[5],  # New Process Name
        "syscall_id": "execve",  # Symbolic syscall tag
        "timestamp": record.TimeGenerated.strftime("%Y-%m-%d %H:%M:%S")
    }

def start_windows_event_monitor(callback):
    print("🧠 Windows Event Monitor started (Security Log, Event ID 4688)")
    server = None  # Local machine
    log_type = SECURITY_LOG
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    while True:
        try:
            handle = win32evtlog.OpenEventLog(server, log_type)
            events = win32evtlog.ReadEventLog(handle, flags, 0)
            for record in events:
                if record.EventID == EVENT_ID:
                    event = parse_event(record)
                    if event:
                        callback(event)
            time.sleep(1)
        except Exception as e:
            print(f"[⚠️] Event monitor error: {e}")
            time.sleep(5)

