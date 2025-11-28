# codex_predictive_dashboard_symbolic.py
# Part 1: Core engine, daemon, predictive logic, and symbolic glyph overlays

import time, random, uuid, psutil, secrets, threading, queue, os
from collections import deque
from statistics import mean, pstdev
import tkinter as tk, matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

event_queue = queue.Queue()

GLYPH_CHARS = "✶✹✸✷✦✧★☆◆◇◈◉☼☯☄☢☣☠☤☥☦☨☩☪☫☬☭☮☯☰☱☲☳☴☵☶☷"

def random_glyph_stream(n=12):
    return [{"char": random.choice(GLYPH_CHARS), "intensity": random.uniform(0.1, 1.0)} for _ in range(n)]

class Engine:
    def __init__(self):
        self.w = [0.6, -0.8, -0.3]
        self.log = []
        self.buf = deque(maxlen=300)
        self.thr = 0.22
        self.mut = 0.06
    def step(self, motion, mag):
        pred = self.w[0]*motion + self.w[1]*mag + self.w[2]*random.uniform(-.02, .02)
        act = motion + 0.85*mag + random.uniform(-.01, .01)
        err = abs(act - pred) / (abs(act) + abs(pred) + 1e-3)
        emo = "dread" if err > 0.25 else "awe" if err < 0.1 else "curiosity"
        self.buf.append({"err": err, "emotion": emo})
        self.mutate(err > self.thr)
        return err, emo
    def mutate(self, ghost):
        inten = self.mut * (2 if ghost else .5)
        delta = [random.uniform(-inten, inten) for _ in self.w]
        self.w = [a + b for a, b in zip(self.w, delta)]
        self.log.append(delta)

class Node:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.e = Engine()
        self.inbox = []
        self.errs = deque(maxlen=300)
    def tick(self, motion, mag):
        err, emo = self.e.step(motion, mag)
        self.errs.append(err)
        return err, emo
    def absorb(self, m): self.inbox.append(m)
    def merge(self):
        if self.inbox:
            self.e.thr = mean([m["thr"] for m in self.inbox] + [self.e.thr])
            self.e.mut = mean([m["mut"] for m in self.inbox] + [self.e.mut])
            self.inbox.clear()

class Swarm:
    def __init__(self, n=5): self.nodes = [Node() for _ in range(n)]
    def broadcast(self):
        msgs = [{"thr": n.e.thr, "mut": n.e.mut, "node": n.id} for n in self.nodes]
        for n in self.nodes:
            for m in msgs:
                if m["node"] != n.id: n.absorb(m)
    def consensus(self): [n.merge() for n in self.nodes]

def sysdata():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return cpu, mem

class DevourerDaemon:
    def __init__(self, path=".", net_interval=5):
        self.stop_event = threading.Event()
        self.path = path
        self.net_interval = net_interval
        self._prev_conns = set()
    def start(self):
        threading.Thread(target=self.monitor_network, daemon=True).start()
    def stop(self): self.stop_event.set()
    def monitor_network(self):
        while not self.stop_event.is_set():
            try:
                conns = {(c.laddr, c.raddr) for c in psutil.net_connections(kind='inet') if c.status == "ESTABLISHED"}
                new = conns - self._prev_conns
                for laddr, raddr in new:
                    event_queue.put(("net", f"Outbound {raddr} from {laddr}"))
                self._prev_conns = conns
            except Exception as e:
                event_queue.put(("error", f"Net error: {e}"))
            time.sleep(self.net_interval)

class RogueAI:
    def __init__(self):
        self.weights = [0.5, -0.3, 0.8]
        self.log = []
        self.glyph_stream = random_glyph_stream()
    def update(self, entropy_level):
        delta = (entropy_level - 0.5) * 0.05
        self.weights = [w + delta for w in self.weights]
        self.log.append(list(self.weights))
        self.glyph_stream = random_glyph_stream()

def forecast_series(series, horizon=20):
    if len(series) < 2: return []
    slope = (series[-1] - series[0]) / max(1, len(series)-1)
    return [series[-1] + slope * i for i in range(1, horizon+1)]

def anomaly_stats(series, window=50):
    if not series: return 0.0, 0.0
    w = series[-min(window, len(series)):]
    mu = mean(w)
    sd = pstdev(w) if len(w) > 1 else 0.0
    return mu, sd

# Part 2: Tkinter GUI with symbolic glyph overlays and rogue drift visualization

class CodexGUI(tk.Tk):
    def __init__(self, swarm, rogue_ai, loop_interval_ms=140):
        super().__init__()
        self.title("Codex Predictive Dashboard (Symbolic)")
        self.geometry("720x540")
        self.swarm = swarm
        self.e = swarm.nodes[0].e
        self.rogue_ai = rogue_ai
        self.errs = []
        self.mut_intensity = []
        self.cpu = []
        self.mem = []
        self.step = 0
        self.last = time.perf_counter()
        self.loop_interval = loop_interval_ms / 1000.0

        # Logs
        self.fs_log = tk.Text(self, height=6, width=60)
        self.fs_log.pack(side="top", fill="x")
        self.net_log = tk.Text(self, height=3, width=60)
        self.net_log.pack(side="top", fill="x")

        # Charts
        self.fig = plt.Figure(figsize=(6.2, 5.2))
        self.ax_err   = self.fig.add_subplot(511)
        self.ax_mut   = self.fig.add_subplot(512)
        self.ax_swarm = self.fig.add_subplot(513)
        self.ax_sys   = self.fig.add_subplot(514)
        self.ax_rogue = self.fig.add_subplot(515)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)

        self.after(loop_interval_ms, self.loop)

    def loop(self):
        now = time.perf_counter()
        dt = now - self.last
        self.last = now

        mag = random.uniform(0.0, 1.0)  # Simulated motion magnitude

        for n in self.swarm.nodes:
            err, emo = n.tick(dt, mag)
            if n is self.swarm.nodes[0]:
                self.errs.append((err, emo))
                if self.e.log: self.mut_intensity.append(sum(abs(x) for x in self.e.log[-1]))

        cpu, mem = sysdata()
        self.cpu.append(cpu)
        self.mem.append(mem)
        self.fs_log.insert("end", f"CPU:{cpu:.1f}% MEM:{mem:.1f}%\n"); self.fs_log.see("end")

        while not event_queue.empty():
            kind, data = event_queue.get()
            if kind == "fs": self.fs_log.insert("end", data + "\n"); self.fs_log.see("end")
            elif kind == "net": self.net_log.insert("end", data + "\n"); self.net_log.see("end")
            elif kind == "error": self.fs_log.insert("end", "ERROR: " + data + "\n"); self.fs_log.see("end")

        # Predictive alerts
        entropy_level = self.generate_predictive_alerts()

        # Rogue AI update
        self.rogue_ai.update(entropy_level)

        if self.step % 20 == 0: self.swarm.broadcast()
        if self.step % 40 == 0: self.swarm.consensus()

        self.draw()
        self.step += 1
        self.after(int(self.loop_interval * 1000), self.loop)

    def generate_predictive_alerts(self):
        err_series = [e[0] for e in self.errs]
        if not err_series: return 0.5
        forecast = forecast_series(err_series, horizon=20)
        max_forecast = max(forecast) if forecast else 0.0
        mu, sd = anomaly_stats(err_series)
        cur = err_series[-1]
        if cur > mu + 2*sd:
            self.fs_log.insert("end", f"⚠️ Error anomaly: {cur:.2f} > μ+2σ\n")
        if max_forecast > 0.3:
            self.fs_log.insert("end", f"⚠️ Forecast spike: {max_forecast:.2f}\n")
        return min(1.0, max_forecast)

    def draw(self):
        # Error chart
        self.ax_err.clear()
        err_series = [e[0] for e in self.errs]
        self.ax_err.plot(err_series, color="black", label="Error")
        forecast = forecast_series(err_series, horizon=20)
        if forecast:
            xs = list(range(len(err_series), len(err_series)+len(forecast)))
            self.ax_err.plot(xs, forecast, color="orange", linestyle="--", label="Forecast")
        self.ax_err.set_title("Error Prediction")
        self.ax_err.legend(fontsize=7)
        self.ax_err.grid(True, alpha=0.3)

        # Mutation intensity
        self.ax_mut.clear()
        self.ax_mut.bar(range(len(self.mut_intensity)), self.mut_intensity, color="purple")
        self.ax_mut.set_title("Mutation Tracking")
        self.ax_mut.grid(True, alpha=0.3)

        # Swarm stability
        self.ax_swarm.clear()
        for i, n in enumerate(self.swarm.nodes):
            avg = sum(n.errs)/len(n.errs) if n.errs else 0
            self.ax_swarm.add_patch(plt.Rectangle((i, 0), 1, 1, color=(min(1, avg*2), 0.5, 0.2)))
            self.ax_swarm.text(i+0.5, 0.5, f"{n.id[:4]} err={avg:.2f}",
                               ha="center", va="center", color="white", fontsize=6)
        self.ax_swarm.set_xlim(0, len(self.swarm.nodes)); self.ax_swarm.set_ylim(0, 1)
        self.ax_swarm.set_title("Swarm Stability")
        self.ax_swarm.axis("off")

        # System telemetry
        self.ax_sys.clear()
        self.ax_sys.plot(self.cpu, color="red", label="CPU")
        self.ax_sys.plot(self.mem, color="blue", label="MEM")
        self.ax_sys.set_title("System Telemetry")
        self.ax_sys.legend(fontsize=7)
        self.ax_sys.grid(True, alpha=0.3)

        # Rogue glyph stream
        self.ax_rogue.clear()
        self.ax_rogue.set_title("Rogue Glyph Stream")
        for i, g in enumerate(self.rogue_ai.glyph_stream):
            self.ax_rogue.text(i, 0.5, g["char"], fontsize=10 + g["intensity"]*10,
                               color=(1-g["intensity"], g["intensity"], 0.5),
                               ha="center", va="center")
        self.ax_rogue.set_xlim(0, len(self.rogue_ai.glyph_stream))
        self.ax_rogue.set_ylim(0, 1)
        self.ax_rogue.axis("off")

        self.canvas.draw()

# --- Run ---
if __name__ == "__main__":
    swarm = Swarm()
    rogue_ai = RogueAI()
    daemon = DevourerDaemon(path=os.getcwd())
    daemon.start()
    try:
        CodexGUI(swarm, rogue_ai).mainloop()
    finally:
        daemon.stop()

