# mythic_symbolic_simulator.py

import sys, threading, time, math, psutil, tkinter as tk
from enum import Enum
from datetime import datetime

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
        self.root.title("Mythic Symbolic Simulator")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")

        self.bit_types = list(BitType)
        self.mutation_states = list(MutationState)
        self.bit_index = 0
        self.mutation_index = 0
        self.running = True
        self.recent_flops = []

        # Header
        tk.Label(root, text="Symbolic FLOP Capsule Engine", fg="#00ffff", bg="#1e1e1e", font=("Courier", 18)).pack(pady=10)

        # Bit & Mutation Display
        self.bit_label = tk.Label(root, text="Bit: ⨂", fg="#ffffff", bg="#1e1e1e", font=("Courier", 22))
        self.bit_label.pack()
        self.state_label = tk.Label(root, text="State: pristine", fg="#aaaaaa", bg="#1e1e1e", font=("Courier", 14))
        self.state_label.pack()

        # FLOP Result
        self.result_label = tk.Label(root, text="FLOPs: ", fg="#00ff00", bg="#1e1e1e", font=("Courier", 16))
        self.result_label.pack(pady=10)

        # Telemetry Panel
        self.telemetry_frame = tk.Frame(root, bg="#1e1e1e")
        self.telemetry_frame.pack(pady=5)

        self.entropy_label = tk.Label(self.telemetry_frame, text="Entropy γ_E: ", fg="#00ffff", bg="#1e1e1e", font=("Courier", 12))
        self.entropy_label.grid(row=0, column=0, padx=10)
        self.time_label = tk.Label(self.telemetry_frame, text="Time Dilation δ_T: ", fg="#ff00ff", bg="#1e1e1e", font=("Courier", 12))
        self.time_label.grid(row=0, column=1, padx=10)

        self.cpu_label = tk.Label(self.telemetry_frame, text="CPU %: ", fg="#ffaa00", bg="#1e1e1e", font=("Courier", 12))
        self.cpu_label.grid(row=1, column=0, padx=10)
        self.mem_label = tk.Label(self.telemetry_frame, text="Memory %: ", fg="#ffaa00", bg="#1e1e1e", font=("Courier", 12))
        self.mem_label.grid(row=1, column=1, padx=10)
        self.gpu_label = tk.Label(self.telemetry_frame, text="GPU Load: ", fg="#ff4444", bg="#1e1e1e", font=("Courier", 12))
        self.gpu_label.grid(row=2, column=0, padx=10)

        # Mutation Lineage
        self.mutation_label = tk.Label(root, text="Mutation: ", fg="#ff00ff", bg="#1e1e1e", font=("Courier", 10))
        self.mutation_label.pack()

        # Execution Log
        self.log_frame = tk.Frame(root, bg="#1e1e1e")
        self.log_frame.pack(pady=10)
        tk.Label(self.log_frame, text="Execution Log", fg="#ffffff", bg="#1e1e1e", font=("Courier", 12)).pack()
        self.log_box = tk.Text(self.log_frame, height=10, width=100, bg="#2e2e2e", fg="#00ffcc", font=("Courier", 10))
        self.log_box.pack()

        # Auto-Rotation Toggle
        self.auto_var = tk.BooleanVar(value=True)
        self.toggle = tk.Checkbutton(root, text="Auto-Rotate Symbolic Bits", variable=self.auto_var, bg="#1e1e1e", fg="white", font=("Courier", 10), command=self.toggle_rotation)
        self.toggle.pack()

        threading.Thread(target=self.autonomous_loop, daemon=True).start()

    def toggle_rotation(self):
        self.running = self.auto_var.get()

    def autonomous_loop(self):
        while True:
            if self.running:
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
                    continue  # Skip this cycle if mutation fails

                flops = calculate_flops(alpha, BASE_FLOP, gamma_E, delta_T, mu_C, mu_M, mu_G)
                self.recent_flops.append(flops)

                # Update GUI
                self.bit_label.config(text=f"Bit: {bit_type.value}")
                self.state_label.config(text=f"State: {mutation_state.value}")
                self.result_label.config(text=f"FLOPs: {flops:.2e}")
                self.entropy_label.config(text=f"Entropy γ_E: {gamma_E}")
                self.time_label.config(text=f"Time Dilation δ_T: {delta_T}")
                self.cpu_label.config(text=f"CPU %: {psutil.cpu_percent()}%")
                self.mem_label.config(text=f"Memory %: {psutil.virtual_memory().percent}%")
                self.gpu_label.config(text=f"GPU Load: {int(mu_G * 100)}%")
                self.mutation_label.config(text=f"Mutation: {mutation_history[-1]}")

                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_box.insert(tk.END, f"[{timestamp}] {bit_type.name}-{mutation_state.name} → {flops:.2e} FLOPs | {mutation_history[-1]}\n")
                self.log_box.see(tk.END)

                # Rotate symbolic states
                self.bit_index = (self.bit_index + 1) % len(self.bit_types)
                self.mutation_index = (self.mutation_index + 1) % len(self.mutation_states)

            time.sleep(2.0)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SymbolicSimulatorGUI(root)
    root.mainloop()



