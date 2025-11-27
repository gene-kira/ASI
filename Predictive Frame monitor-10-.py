# codex_devourer_dashboard_predictive.py
# Codex Predictive Engine + Gamepad + System Telemetry + Filesystem/Network Monitoring
# Predictive forecasting (error and system load) + anomaly alerts, scaled-down GUI

import time, random, uuid, psutil, secrets, threading, queue
from collections import deque
from statistics import median, mean, pstdev
import tkinter as tk, matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
    from inputs import get_gamepad
except:
    get_gamepad = None

# --- Shared event bus ---
event_queue = queue.Queue()

# --- Config ---
INPUT_OVERLAYS = {
    "BTN_SOUTH": ("awe","*"), "BTN_EAST": ("dread","x"),
    "BTN_NORTH": ("curiosity","o"), "BTN_WEST": ("neutral","."),
    "BTN_TL": ("awe","P")
}
ERROR_FORECAST_HORIZON = 20      # future steps to plot
SYS_FORECAST_HORIZON = 30        # future steps to plot
ERROR_PREDICT_THRESHOLD = 0.28   # predicted error warning
CPU_WARN_LEVEL = 85.0
MEM_WARN_LEVEL = 85.0

# --- Core predictive engine ---
class Engine:
    def __init__(self):
        self.w=[0.6,-0.8,-0.3]; self.log=[]; self.buf=deque(maxlen=300)
        self.thr=0.22; self.mut=0.06
    def step(self,motion,mag):
        pred=self.w[0]*motion+self.w[1]*mag+self.w[2]*random.uniform(-.02,.02)
        act=motion+0.85*mag+random.uniform(-.01,.01)
        err=abs(act-pred)/(abs(act)+abs(pred)+1e-3)
        emo="dread" if err>0.25 else "awe" if err<0.1 else "curiosity"
        self.buf.append({"err":err,"emotion":emo})
        self.mutate(err>self.thr); return err,emo
    def mutate(self,ghost):
        inten=self.mut*(2 if ghost else .5)
        delta=[random.uniform(-inten,inten) for _ in self.w]
        self.w=[a+b for a,b in zip(self.w,delta)]
        self.log.append(delta)

class Node:
    def __init__(self):
        self.id=str(uuid.uuid4()); self.e=Engine(); self.inbox=[]; self.errs=deque(maxlen=300)
    def tick(self,motion,mag): err,emo=self.e.step(motion,mag); self.errs.append(err); return err,emo
    def absorb(self,m): self.inbox.append(m)
    def merge(self):
        if self.inbox:
            self.e.thr=median([m["thr"] for m in self.inbox]+[self.e.thr])
            self.e.mut=median([m["mut"] for m in self.inbox]+[self.e.mut]); self.inbox.clear()

class Swarm:
    def __init__(self,n=5): self.nodes=[Node() for _ in range(n)]
    def broadcast(self):
        msgs=[{"thr":n.e.thr,"mut":n.e.mut,"node":n.id} for n in self.nodes]
        for n in self.nodes: [n.absorb(m) for m in msgs if m["node"]!=n.id]
    def consensus(self): [n.merge() for n in self.nodes]

# --- Input + System telemetry ---
def poll_gamepad():
    mag,ovs=0,[]
    if not get_gamepad: return mag,ovs
    try:
        for e in get_gamepad():
            if e.code in ("ABS_X","ABS_Y"): mag=max(mag,abs(e.state)/32768)
            if e.code in INPUT_OVERLAYS and e.state==1: ovs.append(INPUT_OVERLAYS[e.code][1])
    except: pass
    return mag,ovs

def sysdata():
    cpu=psutil.cpu_percent()
    mem=psutil.virtual_memory().percent
    procs=[(p.info["pid"],p.info["name"]) for p in psutil.process_iter(attrs=["pid","name"])][:5]
    return cpu,mem,procs

# --- DevourerDaemon monitors ---
class DevourerDaemon:
    def __init__(self,path=".",net_interval=5,mutate_interval=30):
        self.stop_event=threading.Event()
        self.glyph_key=[0x13,0x37,0x42,0x66]
        self.path=path; self.net_interval=net_interval; self.mutate_interval=mutate_interval
        self._prev_conns=set()
    def start(self):
        threading.Thread(target=self.monitor_filesystem,daemon=True).start()
        threading.Thread(target=self.monitor_network,daemon=True).start()
        threading.Thread(target=self.mutate_glyph_language,daemon=True).start()
    def stop(self): self.stop_event.set()
    def monitor_filesystem(self):
        class Handler(FileSystemEventHandler):
            def on_any_event(_,event):
                if not event.is_directory:
                    event_queue.put(("fs",f"{event.event_type}: {event.src_path}"))
        obs=Observer(); obs.schedule(Handler(),path=self.path,recursive=True); obs.start()
        while not self.stop_event.is_set(): time.sleep(1)
        obs.stop(); obs.join()
    def monitor_network(self):
        while not self.stop_event.is_set():
            try:
                conns={(c.laddr,c.raddr) for c in psutil.net_connections(kind='inet') if c.status=="ESTABLISHED"}
                new=conns-self._prev_conns
                for laddr,raddr in new: event_queue.put(("net",f"Outbound {raddr} from {laddr}"))
                self._prev_conns=conns
            except Exception as e: event_queue.put(("error",f"Net error: {e}"))
            time.sleep(self.net_interval)
    def mutate_glyph_language(self):
        while not self.stop_event.is_set():
            try:
                entropy=secrets.randbelow(1000)
                self.glyph_key=[(k+entropy)%256 for k in self.glyph_key]
                event_queue.put(("glyph",entropy))
            except Exception as e: event_queue.put(("error",f"Mutation error: {e}"))
            time.sleep(self.mutate_interval)

# --- Predictive helpers ---
def compute_slope(series, window=20):
    """Approximate slope per step using last 'window' points."""
    if len(series) < 2: return 0.0
    w = min(window, len(series))
    s = series[-w:]
    return (s[-1] - s[0]) / (w - 1) if w > 1 else 0.0

def forecast_series(series, horizon=20, window=20):
    """Linear forecast using recent slope."""
    if not series: return []
    last = series[-1]
    slope = compute_slope(series, window)
    return [last + slope * i for i in range(1, horizon + 1)]

def anomaly_stats(series, window=50):
    """Return mean and std over window for anomaly detection."""
    if not series: return 0.0, 0.0
    w = series[-min(window, len(series)):]
    mu = mean(w)
    sd = pstdev(w) if len(w) > 1 else 0.0
    return mu, sd

# --- GUI Dashboard (scaled down + predictive overlays) ---
class CodexGUI(tk.Tk):
    def __init__(self,swarm, loop_interval_ms=120):
        super().__init__()
        self.title("Codex + Devourer Dashboard (Predictive, Small)")
        self.geometry("640x440")   # smaller window
        self.swarm=swarm; self.e=swarm.nodes[0].e
        self.errs=[]; self.mut_intensity=[]; self.cpu=[]; self.mem=[]; self.glyph_entropy=[]
        self.step=0; self.last=time.perf_counter(); self.loop_interval=loop_interval_ms/1000.0

        # Logs
        self.fs_log=tk.Text(self,height=6,width=50); self.fs_log.pack(side="top",fill="x")
        self.net_log=tk.Text(self,height=3,width=50); self.net_log.pack(side="top",fill="x")

        # Charts
        self.fig=plt.Figure(figsize=(5.0,4.8))
        self.ax_err=self.fig.add_subplot(411)    # error + forecast
        self.ax_mut=self.fig.add_subplot(412)    # mutation intensity + glyph entropy
        self.ax_swarm=self.fig.add_subplot(413)  # stability
        self.ax_sys=self.fig.add_subplot(414)    # cpu/mem + forecast
        self.canvas=FigureCanvasTkAgg(self.fig,master=self); self.canvas.get_tk_widget().pack(side="bottom",fill="both",expand=True)

        self.after(loop_interval_ms,self.loop)

    def loop(self):
        # time delta approximates motion
        now = time.perf_counter(); dt = now - self.last; self.last = now
        mag,ovs=poll_gamepad()

        # tick swarm
        for n in self.swarm.nodes:
            err,emo=n.tick(dt,mag)
            if n is self.swarm.nodes[0]:
                self.errs.append((err,ovs))
                if self.e.log: self.mut_intensity.append(sum(abs(x) for x in self.e.log[-1]))

        # system telemetry
        cpu,mem,pids=sysdata(); self.cpu.append(cpu); self.mem.append(mem)
        self.fs_log.insert("end",f"CPU:{cpu:.1f}% MEM:{mem:.1f}% PIDS:{pids}\n"); self.fs_log.see("end")

        # drain daemon events
        while not event_queue.empty():
            kind,data=event_queue.get()
            if kind=="fs": self.fs_log.insert("end",data+"\n"); self.fs_log.see("end")
            elif kind=="net": self.net_log.insert("end",data+"\n"); self.net_log.see("end")
            elif kind=="glyph": self.glyph_entropy.append(data)
            elif kind=="error": self.fs_log.insert("end","ERROR: "+data+"\n"); self.fs_log.see("end")

            # predictive glyph mutation accelerates if recent error forecast is high
            # (handled below via alert generation)

        # predictive alerts & glyph coupling
        self.generate_predictive_alerts()

        # periodic swarm ops
        if self.step%20==0: self.swarm.broadcast()
        if self.step%40==0: self.swarm.consensus()

        # redraw charts
        self.draw()
        self.step+=1
        self.after(int(self.loop_interval*1000),self.loop)

    def generate_predictive_alerts(self):
        # Error forecasts
        err_series = [e[0] for e in self.errs]
        err_forecast = forecast_series(err_series, ERROR_FORECAST_HORIZON)
        if err_forecast and max(err_forecast) >= ERROR_PREDICT_THRESHOLD:
            event_queue.put(("fs", f"⚠️ Predicted error spike: max forecast {max(err_forecast):.2f}"))
            # Coupling: append a synthetic glyph entropy "boost"
            self.glyph_entropy.append( min(999, int( (max(err_forecast)-ERROR_PREDICT_THRESHOLD)*1000 )) )

        # Anomaly detection for current error
        mu, sd = anomaly_stats(err_series, window=50)
        if err_series:
            cur = err_series[-1]
            if sd > 0 and cur > mu + 2*sd:
                event_queue.put(("fs", f"⚠️ Error anomaly: {cur:.2f} > μ+2σ ({mu:.2f}+{2*sd:.2f})"))

        # CPU/mem trend forecast
        cpu_fore = forecast_series(self.cpu, SYS_FORECAST_HORIZON)
        mem_fore = forecast_series(self.mem, SYS_FORECAST_HORIZON)

        if cpu_fore and max(cpu_fore) >= CPU_WARN_LEVEL:
            event_queue.put(("fs", f"⚠️ CPU trending high: forecast max {max(cpu_fore):.1f}%"))
        if mem_fore and max(mem_fore) >= MEM_WARN_LEVEL:
            event_queue.put(("fs", f"⚠️ MEM trending high: forecast max {max(mem_fore):.1f}%"))

        # time-to-threshold estimate
        def time_to_threshold(series, threshold):
            if len(series) < 5: return None
            slope = compute_slope(series, window=20)  # per loop step
            if slope <= 0: return None
            remaining = threshold - series[-1]
            if remaining <= 0: return 0.0
            steps = remaining / slope
            return steps * self.loop_interval  # seconds

        cpu_ttt = time_to_threshold(self.cpu, CPU_WARN_LEVEL)
        mem_ttt = time_to_threshold(self.mem, MEM_WARN_LEVEL)
        if cpu_ttt is not None and cpu_ttt > 0:
            event_queue.put(("fs", f"⏳ CPU may reach {CPU_WARN_LEVEL:.0f}% in ~{cpu_ttt:.0f}s"))
        if mem_ttt is not None and mem_ttt > 0:
            event_queue.put(("fs", f"⏳ MEM may reach {MEM_WARN_LEVEL:.0f}% in ~{mem_ttt:.0f}s"))

        # Drain any newly added alerts to logs immediately
        while not event_queue.empty():
            kind,data=event_queue.get()
            if kind=="fs": self.fs_log.insert("end",data+"\n"); self.fs_log.see("end")
            elif kind=="net": self.net_log.insert("end",data+"\n"); self.net_log.see("end")
            elif kind=="glyph": self.glyph_entropy.append(data)
            elif kind=="error": self.fs_log.insert("end","ERROR: "+data+"\n"); self.fs_log.see("end")

    def draw(self):
        # Error chart with glyph overlays and forecast
        self.ax_err.clear()
        err_series = [e[0] for e in self.errs]
        self.ax_err.plot(err_series, color="black", linewidth=1, label="Error")
        [self.ax_err.scatter(i,e[0],marker=ov,s=36,color="orange")
         for i,e in enumerate(self.errs) for ov in e[1]]
        # Forecast overlay
        err_forecast = forecast_series(err_series, ERROR_FORECAST_HORIZON)
        if err_forecast:
            x_start = len(err_series)
            xs = list(range(x_start, x_start + len(err_forecast)))
            self.ax_err.plot(xs, err_forecast, color="red", linestyle="--", label="Forecast")
        self.ax_err.set_title("Prediction error (with forecast)")
        self.ax_err.legend(fontsize=7)
        self.ax_err.grid(True, alpha=0.25)

        # Mutation intensity and glyph entropy
        self.ax_mut.clear()
        self.ax_mut.bar(range(len(self.mut_intensity)), self.mut_intensity, color="purple", label="Σ|Δw|")
        if self.glyph_entropy:
            self.ax_mut.plot(self.glyph_entropy, color="green", linewidth=1, label="Glyph entropy")
        self.ax_mut.set_title("Mutation intensity and glyph entropy")
        self.ax_mut.legend(fontsize=7)
        self.ax_mut.grid(True, alpha=0.25)

        # Swarm stability heatmap
        self.ax_swarm.clear()
        for i,n in enumerate(self.swarm.nodes):
            avg=sum(n.errs)/len(n.errs) if n.errs else 0
            self.ax_swarm.add_patch(plt.Rectangle((i,0),1,1,color=(min(1,avg*2),0.5,0.2)))
            self.ax_swarm.text(i+0.5,0.5,f"{n.id[:4]} err={avg:.2f}",
                               ha="center",va="center",color="white",fontsize=6)
        self.ax_swarm.set_xlim(0,len(self.swarm.nodes)); self.ax_swarm.set_ylim(0,1)
        self.ax_swarm.set_title("Swarm stability")
        self.ax_swarm.set_xticks([]); self.ax_swarm.set_yticks([])

        # System telemetry with forecast
        self.ax_sys.clear()
        self.ax_sys.plot(self.cpu,color="red",label="CPU %")
        self.ax_sys.plot(self.mem,color="blue",label="MEM %")
        cpu_fore = forecast_series(self.cpu, SYS_FORECAST_HORIZON)
        mem_fore = forecast_series(self.mem, SYS_FORECAST_HORIZON)
        if cpu_fore:
            xs = list(range(len(self.cpu), len(self.cpu)+len(cpu_fore)))
            self.ax_sys.plot(xs, cpu_fore, color="red", linestyle="--", alpha=0.8, label="CPU forecast")
        if mem_fore:
            xs = list(range(len(self.mem), len(self.mem)+len(mem_fore)))
            self.ax_sys.plot(xs, mem_fore, color="blue", linestyle="--", alpha=0.8, label="MEM forecast")
        self.ax_sys.set_title("System telemetry (with forecast)")
        self.ax_sys.legend(fontsize=7)
        self.ax_sys.grid(True, alpha=0.25)

        self.canvas.draw()

# --- Run ---
if __name__=="__main__":
    swarm = Swarm()
    daemon = DevourerDaemon(path=".")
    daemon.start()
    try:
        CodexGUI(swarm).mainloop()
    finally:
        daemon.stop()

