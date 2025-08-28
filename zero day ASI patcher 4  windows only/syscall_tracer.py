import random
import time

# Simulated syscall pool
SYSCALLS = ["__NR_execve", "__NR_open", "__NR_socket", "__NR_write", "__NR_read"]

# Simulated process pool
PROCESSES = ["nginx", "python", "curl", "node", "unknown"]

def generate_event():
    return {
        "pid": random.randint(1000, 9999),
        "comm": random.choice(PROCESSES),
        "syscall_id": random.choice(SYSCALLS),
        "timestamp": time.time()
    }

def start_tracer(callback, interval=1.0):
    print("🧪 Simulated syscall tracer started.")
    while True:
        event = generate_event()
        callback(event)
        time.sleep(interval)

