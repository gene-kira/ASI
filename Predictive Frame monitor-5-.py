# codex_inputs_overlays.py
# Predictive Frame Engine + Swarm Consensus + GUI
# Wired to Windows 11 inputs: keyboard, mouse, and XInput controllers.
# Includes symbolic overlays for specific inputs, drawn as glyphs on charts.

import time, math, random, uuid
from collections import deque
from statistics import median

# GUI + plotting
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Gamepad input via XInput
try:
    from inputs import get_gamepad
except ImportError:
    print("Install with: pip install inputs")
    get_gamepad = None

# Mouse + keyboard input
from pynput import keyboard, mouse

# ========= Global input state =========
input_state = {
    "keys": set(),
    "mouse_dx": 0,
    "mouse_dy": 0,
    "mouse_buttons": set()
}

# Symbolic overlays mapping
INPUT_OVERLAYS = {
    "Key.space": ("awe", ["glyph:burst", "aura:gold"]),
    "Key.enter": ("dread", ["glyph:fracture", "aura:black"]),
    "Button.left": ("curiosity", ["glyph:spiral", "aura:blue"]),
    "Button.right": ("neutral", ["glyph:dot", "aura:gray"]),
    "Button.middle": ("awe", ["glyph:star", "aura:purple"])
}

# Glyph markers for chart overlays
GLYPH_MARKERS = {
    "glyph:burst": "*",       # star
    "glyph:spiral": "o",      # circle
    "glyph:fracture": "x",    # cross
    "glyph:dot": ".",         # dot
    "glyph:star": "P"         # filled star
}

# Keyboard listener
def on_press(key):
    try:
        input_state["keys"].add(key.char)
    except AttributeError:
        input_state["keys"].add(str(key))

def on_release(key):
    try:
        input_state["keys"].discard(key.char)
    except AttributeError:
        input_state["keys"].discard(str(key))

# Mouse listener
def on_move(x, y):
    input_state["mouse_dx"] += abs(x)
    input_state["mouse_dy"] += abs(y)

def on_click(x, y, button, pressed):
    if pressed:
        input_state["mouse_buttons"].add(str(button))
    else:
        input_state["mouse_buttons"].discard(str(button))

def on_scroll(x, y, dx, dy):
    input_state["mouse_dx"] += abs(dx)
    input_state["mouse_dy"] += abs(dy)

# Start listeners
keyboard.Listener(on_press=on_press, on_release=on_release).start()
mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll).start()

# ========= Core predictive engine =========
class AdaptiveWeights:
    def __init__(self):
        self.w = [0.6, -0.8, -0.3]
        self.log = []

    def mutate(self, intensity: float, cause: str):
        delta = [random.uniform(-intensity, intensity) for _ in self.w]
        self.w = [a + b for a, b in zip(self.w, delta)]
        self.log.append({"t": time.time(), "delta": delta, "cause": cause})

class Engine:
    def __init__(self):
        self.w = AdaptiveWeights()
        self.buf = deque(maxlen=300)
        self.ghost_threshold = 0.22
        self.mutation_base = 0.06

    def step(self, frame_motion: float, input_mag: float):
        residual = random.uniform(-0.02, 0.02)
        pred_motion = self.w.w[0]*frame_motion + self.w.w[1]*input_mag + self.w.w[2]*residual
        actual_motion = frame_motion + 0.85*input_mag + random.uniform(-0.01, 0.01)
        denom = abs(actual_motion) + abs(pred_motion) + 1e-3
        err = abs(actual_motion - pred_motion) / denom
        emotion = "dread" if err > 0.25 else ("awe" if err < 0.1 else "curiosity")
        self.buf.append({"err": err, "emotion": emotion})
        ghost = err > self.ghost_threshold
        intensity = self.mutation_base * (2.0 if ghost else 0.5)
        self.w.mutate(intensity, "ghost" if ghost else "stable")
        return err, emotion

# ========= Swarm consensus =========
class Node:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.e = Engine()
        self.inbox = []
        self.err_hist = deque(maxlen=150)

    def tick(self, motion: float, input_mag: float):
        err, emo = self.e.step(motion, input_mag)
        self.err_hist.append(err)
        return err, emo

    def absorb(self, msg: dict):
        self.inbox.append(msg)

    def merge_consensus(self):
        if not self.inbox:
            return
        peer_thr = [m["thr"] for m in self.inbox]
        peer_mut = [m["mut"] for m in self.inbox]
        self.e.ghost_threshold = median(peer_thr + [self.e.ghost_threshold])
        self.e.mutation_base = median(peer_mut + [self.e.mutation_base])
        self.inbox.clear()

class Swarm:
    def __init__(self, n=5):
        self.nodes = [Node() for _ in range(n)]

    def broadcast(self):
        msgs = [{"thr": n.e.ghost_threshold, "mut": n.e.mutation_base, "node": n.id} for n in self.nodes]
        for n in self.nodes:
            for m in msgs:
                if m["node"] != n.id:
                    n.absorb(m)

    def consensus_round(self):
        for n in self.nodes:
            n.merge_consensus()

# ========= Unified input polling with overlays =========
def poll_input_mag_and_overlays():
    mag = 0.0
    overlays = []

    # Gamepad
    if get_gamepad:
        try:
            events = get_gamepad()
            for e in events:
                if e.code in ("ABS_X", "ABS_Y"):
                    mag = max(mag, abs(e.state) / 32768.0)
        except Exception:
            pass

    # Keyboard
    for key in list(input_state["keys"]):
        if key in INPUT_OVERLAYS:
            emo, ov = INPUT_OVERLAYS[key]
            overlays.extend(ov)
        mag = max(mag, min(1.0, len(input_state["keys"]) / 10.0))

    # Mouse
    mouse_activity = input_state["mouse_dx"] + input_state["mouse_dy"] + len(input_state["mouse_buttons"])
    for btn in list(input_state["mouse_buttons"]):
        if btn in INPUT_OVERLAYS:
            emo, ov = INPUT_OVERLAYS[btn]
            overlays.extend(ov)
    if mouse_activity > 0:
        mag = max(mag, min(1.0, mouse_activity / 100.0))

    # Reset mouse deltas
    input_state["mouse_dx"] = 0
    input_state["mouse_dy"] = 0

    return mag, overlays

# ========= GUI =========
class CodexGUI(tk.Tk):
    def __init__(self, swarm: Swarm):
        super().__init__()
        self.title("Codex Predictive Frame Monitor (Inputs + Glyph Overlays)")
        self.geometry("1200x780")
        self.swarm = swarm
        self.engine = swarm.nodes[0].e
        self._build_plots()
        self._build_side_panel()
        self.errs = []  # list of (err, overlays)
        self.muts = []
        self.step_i = 0
        self.last_time = time.perf_counter()
        self.after(150, self.loop)

    def _build_plots(self):
        self.fig = plt.Figure(figsize=(8.6, 7.5))
        self.ax_err = self.fig.add_subplot(3, 1, 1)
        self.ax_mut = self.fig.add_subplot(3, 1, 2)
        self.ax_swarm = self.fig.add_subplot(3, 1, 3)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

    def _build_side_panel(self):
        right = ttk.Frame(self); right.pack(side="right", fill="y")
        box = ttk.LabelFrame(right, text="Telemetry Log"); box.pack(fill="both", expand=True, padx=8, pady=8)
        self.log = tk.Text(box, height=32, width=42); self.log.pack(fill="both", expand=True)
        ctrl = ttk.LabelFrame(right, text="Controls"); ctrl.pack(fill="x", padx=8, pady=8)
        ttk.Button(ctrl, text="Broadcast", command=self._do_broadcast).pack(side="left", padx=6, pady=6)
        ttk.Button(ctrl, text="Consensus", command=self._do_consensus).pack(side="left", padx=6, pady=6)
        ttk.Button(ctrl, text="Clear Log", command=lambda: self.log.delete("1.0", "end")).pack(side="left", padx=6, pady=6)
        self.status = tk.StringVar(value="Ready")
        ttk.Label(right, textvariable=self.status).pack(fill="x", padx=8, pady=4)

    def _do_broadcast(self):
        self.swarm.broadcast()
        self._write_log({"event": "broadcast"})
        self.status.set("Swarm broadcast done")

    def _do_consensus(self):
        self.swarm.consensus_round()
        self._write_log({"event": "consensus"})
        self.status.set("Consensus round applied")

    def loop(self):
        # Frame timing
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        motion = dt

        # Unified input magnitude + overlays
        input_mag, overlays = poll_input_mag_and_overlays()

        # Tick swarm
        for n in self.swarm.nodes:
            err, emo = n.tick(motion, input_mag)
            if n is self.swarm.nodes[0]:
                self.errs.append((err, overlays))
                self._write_log({"err": round(err, 4), "emotion": emo, "overlays": overlays})
                if self.engine.w.log:
                    self.muts.append(sum(abs(x) for x in self.engine.w.log[-1]["delta"]))

        # Swarm ops
        if self.step_i % 20 == 0:
            self.swarm.broadcast()
        if self.step_i % 40 == 0:
            self.swarm.consensus_round()

        # Redraw charts
        self._draw_error()
        self._draw_mutation()
        self._draw_swarm_heatmap()

        self.step_i += 1
        self.after(100, self.loop)

    def _write_log(self, entry: dict):
        self.log.insert("end", f"{entry}\n")
        self.log.see("end")

    def _draw_error(self):
        self.ax_err.clear()
        self.ax_err.set_title("Prediction Error Over Time")
        base_errs = [e[0] for e in self.errs]
        self.ax_err.plot(base_errs, color="black", linewidth=1)

        # Overlay glyphs
        for i, (err, overlays) in enumerate(self.errs):
            for ov in overlays:
                if ov in GLYPH_MARKERS:
                    self.ax_err.scatter(i, err, marker=GLYPH_MARKERS[ov], s=80, color="orange")

        self.ax_err.set_ylabel("Error")
        self.ax_err.grid(True, alpha=0.3)

    def _draw_mutation(self):
        self.ax_mut.clear()
        self.ax_mut.set_title("Mutation Intensity (Σ|Δw| per cycle)")
        self.ax_mut.bar(range(len(self.muts)), self.muts, color="purple")
        self.ax_mut.set_ylabel("Σ|Δw|")
        self.ax_mut.grid(True, alpha=0.3)

    def _draw_swarm_heatmap(self):
        self.ax_swarm.clear()
        self.ax_swarm.set_title("Swarm Stability Heatmap")
        self.ax_swarm.set_xticks([]); self.ax_swarm.set_yticks([])
        cols = len(self.swarm.nodes)
        for i, n in enumerate(self.swarm.nodes):
            avg_err = sum(n.err_hist) / len(n.err_hist) if n.err_hist else 0.0
            c = min(1.0, avg_err * 2.0)        # 0 → stable (green), 1 → unstable (red)
            color = (c, 1.0 - c, 0.2)          # RGB mix
            self.ax_swarm.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            self.ax_swarm.text(
                i + 0.5, 0.5,
                f"{n.id[:6]}\nthr={n.e.ghost_threshold:.2f}\nmut={n.e.mutation_base:.2f}\nerr={avg_err:.2f}",
                ha="center", va="center", color="white", fontsize=8
            )
        self.ax_swarm.set_xlim(0, cols); self.ax_swarm.set_ylim(0, 1)
        self.canvas.draw()

# ========= Entry point =========
if __name__ == "__main__":
    swarm = Swarm(n=5)
    app = CodexGUI(swarm)
    app.mainloop()



