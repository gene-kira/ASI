# gui.py
import tkinter as tk
from tkinter import ttk, filedialog
import threading

from scanner import live_data_scan
from mixer import asi_mixer
from mutator import should_mutate, generate_mutated_code
from saver import save_memory, save_mutation
from replicator import sync_mutations
from voice import narrate_fusion, narrate_mutation, narrate_swarm_sync
from overlay import NeuralOverlay

memory_log = []
fusion_output = []
save_path = None

class MagicBoxGUI:
    def __init__(self, root, swarm_path=None):
        self.root = root
        self.swarm_path = swarm_path
        root.title("🧠 MagicBox ASI Interface")
        root.geometry("800x700")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.label = ttk.Label(root, text="MagicBox Sentient Dashboard", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.log = tk.Text(root, height=12, width=100)
        self.log.pack(pady=10)

        self.select_button = ttk.Button(root, text="📁 Select Save Location", command=self.select_save_location)
        self.select_button.pack(pady=5)

        self.save_button = ttk.Button(root, text="💾 Save Knowledge", command=self.save_knowledge)
        self.save_button.pack(pady=5)

        self.clear_button = ttk.Button(root, text="🧹 Clear Log", command=self.clear_log)
        self.clear_button.pack(pady=5)

        self.overlay_frame = tk.Frame(root)
        self.overlay_frame.pack(pady=10)

        self.auto_start()

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def auto_start(self):
        self.log.insert(tk.END, "🧠 Autonomous live scan initializing...\n")
        threading.Thread(target=self.run_live_scan).start()

    def run_live_scan(self):
        global memory_log, fusion_output
        live_memory = live_data_scan()
        memory_log.extend(live_memory)
        fusion_output = asi_mixer(live_memory)
        self.log.insert(tk.END, f"✅ Live scan complete. {len(live_memory)} items tagged.\n")
        self.log.insert(tk.END, f"🧪 ASI Mixer generated {len(fusion_output)} fusion insights.\n")

        narrate_fusion(fusion_output)
        self.visualize_overlay(live_memory + fusion_output)

        if should_mutate(live_memory):
            code, mutation_id = generate_mutated_code(live_memory)
            if save_mutation(code, mutation_id, save_path):
                self.log.insert(tk.END, f"🧬 Mutation {mutation_id} saved to vault.\n")
                narrate_mutation(mutation_id)
                if self.swarm_path:
                    sync_mutations(save_path, self.swarm_path)
                    narrate_swarm_sync()

    def select_save_location(self):
        global save_path
        save_path = filedialog.askdirectory()
        if save_path:
            self.log.insert(tk.END, f"📁 Save location set to: {save_path}\n")

    def save_knowledge(self):
        if save_memory(memory_log, fusion_output, save_path):
            self.log.insert(tk.END, "💾 Knowledge saved successfully.\n")
        else:
            self.log.insert(tk.END, "⚠️ Failed to save knowledge.\n")

    def visualize_overlay(self, memory):
        NeuralOverlay(self.overlay_frame, memory)

    def get_save_path(self):
        return save_path

