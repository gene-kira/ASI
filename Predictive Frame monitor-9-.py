# codex_devourer_dashboard_small.py
# Same functionality, but GUI scaled down ~50%

import time, random, uuid, psutil, secrets, threading, queue
from collections import deque
from statistics import median
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

event_queue = queue.Queue()

INPUT_OVERLAYS = {
    "BTN_SOUTH": ("awe","*"), "BTN_EAST": ("dread","x"),
    "BTN_NORTH": ("curiosity","o"), "BTN_WEST": ("neutral","."),
    "BTN_TL": ("awe","P")
}

# --- Core predictive engine (unchanged) ---
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
        self.id=str(uuid.uuid4()); self.e=Engine(); self.inbox=[]; self.errs=deque(maxlen=150)
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

# --- DevourerDaemon monitors (unchanged) ---
class DevourerDaemon:
    def __init__(self,path="/",net_interval=10,mutate_interval=30):
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

# --- GUI Dashboard (scaled down) ---
class CodexGUI(tk.Tk):
    def __init__(self,swarm):
        super().__init__()
        self.title("Codex + Devourer Dashboard (Small)")
        self.geometry("600x400")   # smaller window
        self.swarm=swarm; self.e=swarm.nodes[0].e
        self.errs=[]; self.muts=[]; self.cpu=[]; self.mem=[]; self.step=0; self.last=time.perf_counter()
        self.fs_log=tk.Text(self,height=5,width=40); self.fs_log.pack(side="top",fill="x")
        self.net_log=tk.Text(self,height=3,width=40); self.net_log.pack(side="top",fill="x")
        self.fig=plt.Figure(figsize=(4.5,4.5))   # smaller plots
        self.ax_err=self.fig.add_subplot(411); self.ax_mut=self.fig.add_subplot(412)
        self.ax_swarm=self.fig.add_subplot(413); self.ax_sys=self.fig.add_subplot(414)
        self.canvas=FigureCanvasTkAgg(self.fig,master=self); self.canvas.get_tk_widget().pack(side="bottom",fill="both",expand=True)
        self.after(150,self.loop)

    def loop(self):
        dt=time.perf_counter()-self.last; self.last=time.perf_counter()
        mag,ovs=poll_gamepad()
        for n in self.swarm.nodes:
            err,emo=n.tick(dt,mag)
            if n is self.swarm.nodes[0]:
                self.errs.append((err,ovs))
                if self.e.log: self.muts.append(sum(abs(x) for x in self.e.log[-1]))
        cpu,mem,pids=sysdata(); self.cpu.append(cpu); self.mem.append(mem)
        self.fs_log.insert("end",f"CPU:{cpu}% MEM:{mem}% PIDS:{pids}\n"); self.fs_log.see("end")
        while not event_queue.empty():
            kind,data=event_queue.get()
            if kind=="fs": self.fs_log.insert("end",data+"\n"); self.fs_log.see("end")
            elif kind=="net": self.net_log.insert("end",data+"\n"); self.net_log.see("end")
            elif kind=="glyph": self.muts.append(data)
            elif kind=="error": self.fs_log.insert("end","ERROR: "+data+"\n"); self.fs_log.see("end")
        if self.step%20==0: self.swarm.broadcast()
        if self.step%40==0: self.swarm.consensus()
        self.draw(); self.step+=1; self.after(100,self.loop)

    def draw(self):
        self.ax_err.clear(); self.ax_err.plot([e[0] for e in self.errs],color="black")
        [self.ax_err.scatter(i,e[0],marker=ov,s=40,color="orange")
         for i,e in enumerate(self.errs) for ov in e[1]]

        self.ax_mut.clear()
        self.ax_mut.bar(range(len(self.muts)), self.muts, color="purple")
        self.ax_mut.set_title("Mutation Intensity")

        self.ax_swarm.clear()
        for i,n in enumerate(self.swarm.nodes):
            avg=sum(n.errs)/len(n.errs) if n.errs else 0
            self.ax_swarm.add_patch(
                plt.Rectangle((i,0),1,1,color=(min(1,avg*2),0.5,0.2))
            )
            self.ax_swarm.text(i+0.5,0.5,f"{n.id[:4]} err={avg:.2f}",
                               ha="center",va="center",color="white",fontsize=6)
        self.ax_swarm.set_xlim(0,len(self.swarm.nodes)); self.ax_swarm.set_ylim(0,1)
        self.ax_swarm.set_title("Swarm Stability")

        self.ax_sys.clear()
        self.ax_sys.plot(self.cpu,color="red",label="CPU %")
        self.ax_sys.plot(self.mem,color="blue",label="MEM %")
        self.ax_sys.set_title("System Telemetry")
        self.ax_sys.legend(fontsize=6)
        self.canvas.draw()

# --- Run ---
if __name__=="__main__":
    swarm = Swarm()
    daemon = DevourerDaemon()
    daemon.start()
    try:
        CodexGUI(swarm).mainloop()
    finally:
        daemon.stop()



