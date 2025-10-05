# symbolic_telemetry_simulator_compact.py

import sys, threading, time, math, psutil, tkinter as tk
from enum import Enum
from datetime import datetime

# Optional GPU support
try:
    import GPUtil
    gpu_available = True
except ImportError:
    gpu_available = False

# 🧬 Symbolic Registry
class BitType(Enum):
    FUSION = '⨂'
    XOR = '⊕'
    TENSOR = '⊗'
    GRADIENT = '∇'
    PRIMAL = '●'
    VOID = '∅'

class MutationState(Enum):
    PRISTINE = 'pristine'
    FUSED = 'fused'
    DECAYED = 'decayed'
    RESONANT = 'resonant'
    CHAOTIC = 'chaotic'

# 🔹 α_B Multiplier Matrix
alpha_B_map = {
    BitType.FUSION: {MutationState.PRISTINE: 1280, MutationState.FUSED: 2048, MutationState.DECAYED: 640, MutationState.RESONANT: 4096, MutationState.CHAOTIC: 8192},
    BitType.XOR: {MutationState.PRISTINE: 320, MutationState.FUSED: 512, MutationState.DECAYED: 160, MutationState.RESONANT: 1024, MutationState.CHAOTIC: 2048},
    BitType.TENSOR: {MutationState.PRISTINE: 512, MutationState.FUSED: 1024, MutationState.DECAYED: 256, MutationState.RESONANT: 2048, MutationState.CHAOTIC: 4096},
    BitType.GRADIENT: {MutationState.PRISTINE: 256, MutationState.FUSED: 512, MutationState.DECAYED: 128, MutationState.RESONANT: 1024, MutationState.CHAOTIC: 2048},
    BitType.PRIMAL: {MutationState.PRISTINE: 64, MutationState.FUSED: 128, MutationState.DECAYED: 32, MutationState.RESONANT: 256, MutationState.CHAOTIC: 512},
    BitType.VOID: {MutationState.PRISTINE: 0, MutationState.FUSED: 0, MutationState.DECAYED: 0, MutationState.RESONANT: 0, MutationState.CHAOTIC: 0}
}

BASE_FLOP = 10**12

# 🔸 FLOP Capsule Calculator
def get_entropy():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    temp = 50  # Placeholder
    return round((cpu + mem + temp) / 300, 2)

def get_time_dilation():
    load = psutil.getloadavg()[0]
    return round(1.0 + math.sin(load / 10), 2)

def get_cpu_multiplier():
    return round(psutil.cpu_percent() / 100, 2)

def get_memory_multiplier():
    return round(psutil.virtual_memory().percent / 100, 2)

def get_gpu_multiplier():
    if gpu_available:
        gpus = GPUtil.getGPUs()
        if gpus:
            return round(gpus[0].load, 2)
    return 1.0

def calculate_flops(bit_type, mutation_state, gamma_E, delta_T):
    alpha = alpha_B_map.get(bit_type, {}).get(mutation_state, 0)
    mu_C = get_cpu_multiplier()
    mu_M = get_memory_multiplier()
    mu_G = get_gpu_multiplier()
    return alpha * BASE_FLOP * gamma_E * delta_T * mu_C * mu_M * mu_G

# 🎛 GUI Class
class SymbolicSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbolic Simulator")
        self.root.geometry("450x300")
        self.root.configure(bg="#1e1e1e")

        self.bit_types = list(BitType)
        self.mutation_states = list(MutationState)
        self.bit_index = 0
        self.mutation_index = 0
        self.running = True

        # Header
        tk.Label(root, text="FLOP Capsule Engine", fg="#00ffff", bg="#1e1e1e", font=("Courier", 10)).pack(pady=5)

        # Bit & Mutation Display
        self.bit_label = tk.Label(root, text="Bit: ⨂", fg="#ffffff", bg="#1e1e1e", font=("Courier", 12))
        self.bit_label.pack()
        self.state_label = tk.Label(root, text="State: pristine", fg="#aaaaaa", bg="#1e1e1e", font=("Courier", 9))
        self.state_label.pack()

        # FLOP Result
        self.result_label = tk.Label(root, text="FLOPs: ", fg="#00ff00", bg="#1e1e1e", font=("Courier", 10))
        self.result_label.pack(pady=5)

        # Telemetry Panel
        self.telemetry_frame = tk.Frame(root, bg="#1e1e1e")
        self.telemetry_frame.pack(pady=2)

        self.entropy_label = tk.Label(self.telemetry_frame, text="γ_E: ", fg="#00ffff", bg="#1e1e1e", font=("Courier", 8))
        self.entropy_label.grid(row=0, column=0, padx=5)
        self.time_label = tk.Label(self.telemetry_frame, text="δ_T: ", fg="#ff00ff", bg="#1e1e1e", font=("Courier", 8))
        self.time_label.grid(row=0, column=1, padx=5)

        self.cpu_label = tk.Label(self.telemetry_frame, text="CPU %: ", fg="#ffaa00", bg="#1e1e1e", font=("Courier", 8))
        self.cpu_label.grid(row=1, column=0, padx=5)
        self.mem_label = tk.Label(self.telemetry_frame, text="Mem %: ", fg="#ffaa00", bg="#1e1e1e", font=("Courier", 8))
        self.mem_label.grid(row=1, column=1, padx=5)
        self.gpu_label = tk.Label(self.telemetry_frame, text="GPU: ", fg="#ff4444", bg="#1e1e1e", font=("Courier", 8))
        self.gpu_label.grid(row=2, column=0, padx=5)

        # Execution Log
        self.log_frame = tk.Frame(root, bg="#1e1e1e")
        self.log_frame.pack(pady=5)
        tk.Label(self.log_frame, text="Log", fg="#ffffff", bg="#1e1e1e", font=("Courier", 8)).pack()
        self.log_box = tk.Text(self.log_frame, height=5, width=50, bg="#2e2e2e", fg="#00ffcc", font=("Courier", 7))
        self.log_box.pack()

        threading.Thread(target=self.autonomous_loop, daemon=True).start()

    def autonomous_loop(self):
        while self.running:
            bit_type = self.bit_types[self.bit_index]
            mutation_state = self.mutation_states[self.mutation_index]

            gamma_E = get_entropy()
            delta_T = get_time_dilation()
            flops = calculate_flops(bit_type, mutation_state, gamma_E, delta_T)

            # Update GUI
            self.bit_label.config(text=f"Bit: {bit_type.value}")
            self.state_label.config(text=f"State: {mutation_state.value}")
            self.result_label.config(text=f"FLOPs: {flops:.2e}")
            self.entropy_label.config(text=f"γ_E: {gamma_E}")
            self.time_label.config(text=f"δ_T: {delta_T}")
            self.cpu_label.config(text=f"CPU %: {psutil.cpu_percent()}%")
            self.mem_label.config(text=f"Mem %: {psutil.virtual_memory().percent}%")
            self.gpu_label.config(text=f"GPU: {int(get_gpu_multiplier()*100)}%")

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_box.insert(tk.END, f"[{timestamp}] {bit_type.name}-{mutation_state.name} → {flops:.2e} FLOPs\n")
            self.log_box.see(tk.END)

            self.bit_index = (self.bit_index + 1) % len(self.bit_types)
            self.mutation_index = (self.mutation_index + 1) % len(self.mutation_states)

            time.sleep(2.0)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SymbolicSimulatorGUI(root)
    root.mainloop()

