# symbolic_mutation_simulator.py

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

alpha_B_map = {
    BitType.FUSION: {MutationState.PRISTINE: 1280, MutationState.FUSED: 2048, MutationState.DECAYED: 640, MutationState.RESONANT: 4096, MutationState.CHAOTIC: 8192},
    BitType.XOR: {MutationState.PRISTINE: 320, MutationState.FUSED: 512, MutationState.DECAYED: 160, MutationState.RESONANT: 1024, MutationState.CHAOTIC: 2048},
    BitType.TENSOR: {MutationState.PRISTINE: 512, MutationState.FUSED: 1024, MutationState.DECAYED: 256, MutationState.RESONANT: 2048, MutationState.CHAOTIC: 4096},
    BitType.GRADIENT: {MutationState.PRISTINE: 256, MutationState.FUSED: 512, MutationState.DECAYED: 128, MutationState.RESONANT: 1024, MutationState.CHAOTIC: 2048},
    BitType.PRIMAL: {MutationState.PRISTINE: 64, MutationState.FUSED: 128, MutationState.DECAYED: 32, MutationState.RESONANT: 256, MutationState.CHAOTIC: 512},
    BitType.VOID: {MutationState.PRISTINE: 0, MutationState.FUSED: 0, MutationState.DECAYED: 0, MutationState.RESONANT: 0, MutationState.CHAOTIC: 0}
}

BASE_FLOP = 10**12
mutation_history = []

# 🔧 System Metrics
def get_entropy():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    temp = 50
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

# 🔁 Mutation Engine
def evolve_formula(entropy, flops_history):
    if entropy > 1.2 and max(flops_history) < 1e15:
        mutation_history.append("Injected symbolic resonance multiplier (×1.5)")
        return """
def calculate_flops(alpha, base_flop, gamma_E, delta_T, mu_C, mu_M, mu_G):
    resonance = 1.5
    return alpha * base_flop * gamma_E * delta_T * mu_C * mu_M * mu_G * resonance
"""
    elif entropy < 0.6:
        mutation_history.append("Reduced FLOP sensitivity (×0.8)")
        return """
def calculate_flops(alpha, base_flop, gamma_E, delta_T, mu_C, mu_M, mu_G):
    return alpha * base_flop * gamma_E * delta_T * mu_C * mu_M * mu_G * 0.8
"""
    else:
        mutation_history.append("Default FLOP formula")
        return """
def calculate_flops(alpha, base_flop, gamma_E, delta_T, mu_C, mu_M, mu_G):
    return alpha * base_flop * gamma_E * delta_T * mu_C * mu_M * mu_G
"""

# 🎛 GUI Class
class SymbolicSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Self-Mutating Symbolic Simulator")
        self.root.geometry("500x350")
        self.root.configure(bg="#1e1e1e")

        self.bit_types = list(BitType)
        self.mutation_states = list(MutationState)
        self.bit_index = 0
        self.mutation_index = 0
        self.running = True
        self.recent_flops = []

        # GUI Elements
        tk.Label(root, text="FLOP Capsule Engine", fg="#00ffff", bg="#1e1e1e", font=("Courier", 12)).pack(pady=5)
        self.bit_label = tk.Label(root, text="Bit: ⨂", fg="#ffffff", bg="#1e1e1e", font=("Courier", 14))
        self.bit_label.pack()
        self.state_label = tk.Label(root, text="State: pristine", fg="#aaaaaa", bg="#1e1e1e", font=("Courier", 10))
        self.state_label.pack()
        self.result_label = tk.Label(root, text="FLOPs: ", fg="#00ff00", bg="#1e1e1e", font=("Courier", 10))
        self.result_label.pack(pady=5)

        self.mutation_label = tk.Label(root, text="Mutation: ", fg="#ff00ff", bg="#1e1e1e", font=("Courier", 8))
        self.mutation_label.pack()

        self.log_box = tk.Text(root, height=8, width=60, bg="#2e2e2e", fg="#00ffcc", font=("Courier", 8))
        self.log_box.pack()

        threading.Thread(target=self.autonomous_loop, daemon=True).start()

    def autonomous_loop(self):
        while self.running:
            bit_type = self.bit_types[self.bit_index]
            mutation_state = self.mutation_states[self.mutation_index]

            gamma_E = get_entropy()
            delta_T = get_time_dilation()
            mu_C = get_cpu_multiplier()
            mu_M = get_memory_multiplier()
            mu_G = get_gpu_multiplier()

            alpha = alpha_B_map.get(bit_type, {}).get(mutation_state, 0)
            formula_code = evolve_formula(gamma_E, self.recent_flops[-5:])
            try:
                exec(formula_code, globals())
            except Exception as e:
                mutation_history.append(f"Mutation failed: {e}")

            flops = calculate_flops(alpha, BASE_FLOP, gamma_E, delta_T, mu_C, mu_M, mu_G)
            self.recent_flops.append(flops)

            # Update GUI
            self.bit_label.config(text=f"Bit: {bit_type.value}")
            self.state_label.config(text=f"State: {mutation_state.value}")
            self.result_label.config(text=f"FLOPs: {flops:.2e}")
            self.mutation_label.config(text=f"Mutation: {mutation_history[-1]}")

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_box.insert(tk.END, f"[{timestamp}] {bit_type.name}-{mutation_state.name} → {flops:.2e} FLOPs | {mutation_history[-1]}\n")
            self.log_box.see(tk.END)

            self.bit_index = (self.bit_index + 1) % len(self.bit_types)
            self.mutation_index = (self.mutation_index + 1) % len(self.mutation_states)

            time.sleep(2.0)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SymbolicSimulatorGUI(root)
    root.mainloop()

