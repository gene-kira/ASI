from bcc import BPF

bpf_code = """
#include <uapi/linux/ptrace.h>
struct data_t {
    u32 pid;
    char comm[16];
};
BPF_PERF_OUTPUT(events);

int trace_execve(struct pt_regs *ctx) {
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

def start_probe(callback):
    b = BPF(text=bpf_code)
    b.attach_kprobe(event="sys_execve", fn_name="trace_execve")
    def handler(cpu, data, size):
        event = b["events"].event(data)
        callback({
            "pid": event.pid,
            "comm": event.comm.decode("utf-8"),
            "syscall_id": "__NR_execve"
        })
    b["events"].open_perf_buffer(handler)
    while True:
        b.perf_buffer_poll()

