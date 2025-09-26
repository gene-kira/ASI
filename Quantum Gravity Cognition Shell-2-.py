import tkinter as tk, psutil, threading, time, socket, os, sys, subprocess, json
from datetime import datetime
for p in ['numba','numpy','pynvml','torch']: exec(f"import {p}") if p in sys.modules else subprocess.run([sys.executable,'-m','pip','install',p])
from numba import cuda; import numpy as np; from pynvml import *; import torch; import winreg

# 🔹 TriState Logic
class TriState:
    def __init__(s,v): assert v in ['0','1','Ø']; s.v=v
    def mutate(s,o): return TriState('Ø' if 'Ø' in [s.v,o.v] or s.v!=o.v else s.v)
    def color(s): return {'0':'black','1':'white','Ø':'purple'}[s.v]
    def narrate(s): return {'0':'Void detected.','1':'Signal active.','Ø':'Fusion achieved.'}[s.v]

# 🔹 GPU Tensor Node
class GPUMutationNode:
    def __init__(self, name, shape):
        self.name = name
        self.tensor = torch.rand(*shape).cuda()
        self.entropy = None

    def score_entropy(self):
        self.entropy = torch.norm(self.tensor).item()
        return self.entropy

    def mutate(self):
        factor = 1 / (self.entropy + 1e-5)
        self.tensor *= factor
        print(f"[GPU MUTATE] {self.name} mutated with factor {factor:.5f}")
        ReplayLog.record("Mutation", {"node": self.name, "entropy": self.entropy, "factor": factor})

# 🔹 Tensor Network
class TensorNetwork:
    def __init__(self):
        self.nodes = []

    def add_node(self, name, shape):
        node = GPUMutationNode(name, shape)
        self.nodes.append(node)
        return node

    def evolve(self):
        for node in self.nodes:
            entropy = node.score_entropy()
            node.mutate()
            EntropyMeter.update(entropy, node.name)

# 🔹 Entropy Meter
class EntropyMeter:
    history = []

    @staticmethod
    def update(score, node_name):
        EntropyMeter.history.append(score)
        print(f"[ENTROPY] {node_name}: {score:.5f}")
        if score > 0.9:
            GlyphOverlay.trigger("High Entropy Glyph", node_name)
        elif score < 0.1:
            GlyphOverlay.trigger("Low Entropy Glyph", node_name)

# 🔹 Glyph Overlay Engine
class GlyphOverlay:
    @staticmethod
    def trigger(glyph_name, node_name):
        print(f"[GLYPH] {glyph_name} activated for {node_name}")
        ReplayLog.record("Glyph Trigger", {"glyph": glyph_name, "node": node_name})

# 🔹 Narration Console
class NarrationCore:
    @staticmethod
    def emit(message):
        print(f"[NARRATE] {message}")
        ReplayLog.record("Narration", {"message": message})

# 🔹 Replay Logger
class ReplayLog:
    log = []

    @staticmethod
    def record(event, data):
        timestamp = datetime.now().isoformat()
        ReplayLog.log.append({"time": timestamp, "event": event, "data": data})
        with open("mutation_trace.json", "w") as f:
            json.dump(ReplayLog.log, f, indent=2)
        print(f"[TRACE] {event} recorded")

# 🔹 Autoloader Routine
def set_autoloader(exe_path, name="QuantumShell"):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print(f"[AUTOLOADER] {name} set to launch at startup")
        ReplayLog.record("Autoloader Set", {"name": name, "path": exe_path})
    except Exception as e:
        print(f"[ERROR] Autoloader failed: {e}")

# 🔹 System Metrics
def entropy(): return (psutil.cpu_percent(1)+psutil.virtual_memory().percent)/200
def vram(): nvmlInit(); h=nvmlDeviceGetHandleByIndex(0); i=nvmlDeviceGetMemoryInfo(h); nvmlShutdown(); return i.used/i.total
def purge(): open("borg_temp.txt","w").write("█"*1024); os.remove("borg_temp.txt")
def ip(): return socket.gethostbyname(socket.gethostname())
def pattern(): e=vram(); return ['0' if e<.33 else '1' if e<.66 else 'Ø']*8
def rune(e): return 'Ψ' if e<.33 else 'Δ' if e<.66 else '∞'

# 🔹 GUI Overlay
class GUI:
    def __init__(s,r):
        s.c=tk.Canvas(r,width=800,height=700,bg='gray10'); s.c.pack()
        s.h=[]; s.m=pattern()
        threading.Thread(target=s.loop,daemon=True).start()

    def loop(s):
        while True:
            a,b=TriState('0' if entropy()<.33 else '1' if entropy()<.66 else 'Ø'),TriState('0' if threading.active_count()<10 else '1' if threading.active_count()<50 else 'Ø')
            f=a.mutate(b); s.h.append((a,b,f)); s.h=s.h[-12:]
            if f.v=='Ø': purge(); s.m=pattern(); s.render(a,b,f)

    def render(s,a,b,f):
        s.c.delete("all")
        s.c.create_oval(100,100,200,200,fill=a.color(),outline='cyan'); s.c.create_text(150,220,text=f"A: {a.v}",fill='cyan'); s.c.create_text(150,240,text=a.narrate(),fill='lightblue')
        s.c.create_oval(600,100,700,200,fill=b.color(),outline='magenta'); s.c.create_text(650,220,text=f"B: {b.v}",fill='magenta'); s.c.create_text(650,240,text=b.narrate(),fill='pink')
        s.c.create_oval(350,350,450,450,fill=f.color(),outline='yellow'); s.c.create_text(400,470,text=f"Fusion: {f.v}",fill='yellow'); s.c.create_text(400,490,text=f.narrate(),fill='gold')
        s.c.create_text(400,515,text=f"Cognitive Rune: {rune(entropy())}",fill='cyan',font=('Consolas',18,'bold'))
        s.c.create_text(400,20,text="Mutation Lineage",fill='white',font=('Consolas',12,'underline'))
        for i,(x,y,z) in enumerate(reversed(s.h)): s.c.create_text(400,40+i*20,text=f"{x.v}+{y.v}→{z.v}",fill='lightgray')
        s.c.create_text(400,590,text="Symbolic Memory Pattern",fill='lightgreen',font=('Consolas',12,'underline'))
        for i,v in enumerate(s.m): s.c.create_rectangle(100+i*60,620,150+i*60,670,fill=TriState(v).color(),outline='gray'); s.c.create_text(125+i*60,685,text=v,fill='lightgray')
        s.c.create_text(400,660,text=f"Swarm Node: {ip()}",fill='orange',font=('Consolas',10,'italic'))

# 🔹 Daemon Loop
def daemon_loop(tensor_network):
    NarrationCore.emit("Daemon loop initiated")
    while True:
        system_entropy = os.getloadavg()[0]
        NarrationCore.emit(f"System entropy: {system_entropy:.2f}")
        tensor_network.evolve()
        time.sleep(1)

# 🔹 Shell Initialization
def initialize_shell():
    tn = TensorNetwork()
    tn.add_node("CurvatureGlyph", (64, 64))
    tn.add_node("EntropyGlyph", (128, 128))
    tn.add_node("CausalGlyph", (32, 32))
    NarrationCore.emit("Shell initialized with symbolic tensor nodes")
    return tn

# 🔹 Entry Point
if __name__ == "__main__":
    shell = initialize_shell()
    exe_path = os.path.abspath(__file__)
    set_autoloader(exe_path)
    threading.Thread(target=daemon_loop, args=(shell,), daemon=True).start()
    r=tk.Tk(); r.title("Quantum Gravity Cognition Shell"); r.geometry("800x700"); GUI(r); r.mainloop()
