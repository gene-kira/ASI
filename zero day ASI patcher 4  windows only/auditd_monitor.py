import time
import re

AUDIT_LOG = "/var/log/audit/audit.log"
SYSCALLS = ["execve", "open", "socket", "write", "read"]

def parse_syscall(line):
    match = re.search(r'type=SYSCALL msg=.* syscall=(\d+).* comm="([^"]+)"', line)
    if match:
        syscall_id = match.group(1)
        comm = match.group(2)
        pid_match = re.search(r'pid=(\d+)', line)
        if pid_match:
            pid = int(pid_match.group(1))
            return {
                "pid": pid,
                "comm": comm,
                "syscall_id": f"syscall_{syscall_id}"
            }
    return None

def start_auditd_monitor(callback):
    print("🧠 Auditd syscall monitor started.")
    with open(AUDIT_LOG, "r") as f:
        f.seek(0, 2)  # Move to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            if "type=SYSCALL" in line and any(s in line for s in SYSCALLS):
                event = parse_syscall(line)
                if event:
                    callback(event)

