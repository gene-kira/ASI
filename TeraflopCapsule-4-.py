# enhanced_symbolic_simulator_gui.py

import sys, threading, time, math, psutil, tkinter as tk
from enum import Enum
from datetime import datetime

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

def calculate_flops(bit_type, mutation_state, gamma_E=1.0, delta_T=1.0):
    alpha = alpha_B_map.get(bit_type, {}).get(mutation_state, 0)
    return alpha * BASE_FLOP * gamma_E * delta_T

def get_entropy():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    temp = 50  # Placeholder
    return round((cpu + mem + temp) / 300, 2)

def get_time_dilation():
    load = psutil.getloadavg()[0]
    return round(1.0 + math.sin(load / 10), 2)

# 🎛 GUI Class
class SymbolicSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbolic CPU/GPU Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        self.bit_types = list(BitType)
        self.mutation_states = list(MutationState)
        self.bit_index = 0
        self.mutation_index = 0
        self.running = True

        # Top Panel
        self.header = tk.Label(root, text="Symbolic FLOP Capsule Engine", fg="#00ffff", bg="#1e1e1e", font=("Courier", 16))
        self.header.pack(pady=10)

        # Bit & Mutation Display
        self.bit_label = tk.Label(root, text="Bit: ⨂", fg="#ffffff", bg="#1e1e1e", font=("Courier", 20))
        self.bit_label.pack()
        self.state_label = tk.Label(root, text="State: pristine", fg="#aaaaaa", bg="#1e1e1e", font=("Courier", 14))
        self.state_label.pack()

        # FLOP Result
        self.result_label = tk.Label(root, text="FLOPs: ", fg="#00ff00", bg="#1e1e1e", font=("Courier", 14))
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

        # Execution Log
        self.log_frame = tk.Frame(root, bg="#1e1e1e")
        self.log_frame.pack(pady=10)
        self.log_label = tk.Label(self.log_frame, text="Execution Log", fg="#ffffff", bg="#1e1e1e", font=("Courier", 12))
        self.log_label.pack()
        self.log_box = tk.Text(self.log_frame, height=10, width=80, bg="#2e2e2e", fg="#00ffcc", font=("Courier", 10))
        self.log_box.pack()

        # Cycle Timer
        self.cycle_label = tk.Label(root, text="Cycle Time: 2.0s", fg="#8888ff", bg="#1e1e1e", font=("Courier", 10))
        self.cycle_label.pack()

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
                flops = calculate_flops(bit_type, mutation_state, gamma_E, delta_T)

                # Update GUI
                self.bit_label.config(text=f"Bit: {bit_type.value}")
                self.state_label.config(text=f"State: {mutation_state.value}")
                self.result_label.config(text=f"FLOPs: {flops:.2e}")
                self.entropy_label.config(text=f"Entropy γ_E: {gamma_E}")
                self.time_label.config(text=f"Time Dilation δ_T: {delta_T}")
                self.cpu_label.config(text=f"CPU %: {psutil.cpu_percent()}%")
                self.mem_label.config(text=f"Memory %: {psutil.virtual_memory().percent}%")

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

