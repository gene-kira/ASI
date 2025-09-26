import tkinter as tk, threading, time, socket, os, sys, subprocess, json, psutil
from datetime import datetime
for p in ['numba','numpy','pynvml','torch']:
    exec(f"import {p}") if p in sys.modules else subprocess.run([sys.executable,'-m','pip','install',p])
from numba import cuda; import numpy as np; from pynvml import *; import torch; import winreg

cuda_ok = torch.cuda.is_available()
def entropy(): return (psutil.cpu_percent(1)+psutil.virtual_memory().percent)/200
def vram(): nvmlInit(); h=nvmlDeviceGetHandleByIndex(0); i=nvmlDeviceGetMemoryInfo(h); nvmlShutdown(); return i.used/i.total
def ip(): return socket.gethostbyname(socket.gethostname())
def rune(e): return 'Ψ' if e<.33 else 'Δ' if e<.66 else '∞'
def pattern(): e=vram(); return ['0' if e<.33 else '1' if e<.66 else 'Ø']*8
def purge(): open("borg_temp.txt","w",encoding="utf-8").write("█"*1024); os.remove("borg_temp.txt")

class TriState:
    def __init__(s,v): s.v=v
    def mutate(s,o): return TriState('Ø' if 'Ø' in [s.v,o.v] or s.v!=o.v else s.v)
    def color(s): return {'0':'black','1':'white','Ø':'purple'}[s.v]
    def narrate(s): return {'0':'Void detected.','1':'Signal active.','Ø':'Fusion achieved.'}[s.v]

class MutationNode:
    def __init__(s,n,sh): s.name=n; s.t=torch.rand(*sh).cuda() if cuda_ok else np.random.rand(*sh)
    def score(s): return torch.norm(s.t).item() if cuda_ok else np.linalg.norm(s.t)
    def mutate(s): f=1/(s.score()+1e-5); s.t*=f; log("Mutation",{"node":s.name,"factor":f})

class TensorNetwork:
    def __init__(s): s.nodes=[]
    def add(s,n,sh): s.nodes.append(MutationNode(n,sh))
    def evolve(s): [n.mutate() for n in s.nodes]

def log(e,d):
    t=datetime.now().isoformat()
    L.append({"time":t,"event":e,"data":d})
    with open("mutation_trace.json","w",encoding="utf-8") as f:
        json.dump(L,f,indent=2,ensure_ascii=False)
    print(f"[TRACE] {e} recorded")

def set_autoloader(p,n="QuantumShell"):
    try:
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k,n,0,winreg.REG_SZ,p); winreg.CloseKey(k); log("Autoloader Set",{"name":n,"path":p})
    except: pass

class GUI:
    def __init__(s,r):
        s.c=tk.Canvas(r,width=800,height=700,bg='gray10'); s.c.pack(); s.h=[]; s.m=pattern()
        threading.Thread(target=s.loop,daemon=True).start()
        threading.Thread(target=s.redraw,daemon=True).start()

    def loop(s):
        while True:
            a=TriState('0' if entropy()<.33 else '1' if entropy()<.66 else 'Ø')
            b=TriState('0' if threading.active_count()<10 else '1' if threading.active_count()<50 else 'Ø')
            f=a.mutate(b); s.h.append((a,b,f)); s.h=s.h[-12:]
            if f.v=='Ø': purge(); s.m=pattern()
            s.render(a,b,f); time.sleep(1)

    def redraw(s):
        while True:
            try: s.c.update_idletasks(); s.c.update()
            except: pass; time.sleep(0.5)

    def render(s,a,b,f):
        s.c.delete("all")
        s.c.create_oval(100,100,200,200,fill=a.color(),outline='cyan')
        s.c.create_text(150,220,text=f"A: {a.v}",fill='cyan')
        s.c.create_text(150,240,text=a.narrate(),fill='lightblue')
        s.c.create_oval(600,100,700,200,fill=b.color(),outline='magenta')
        s.c.create_text(650,220,text=f"B: {b.v}",fill='magenta')
        s.c.create_text(650,240,text=b.narrate(),fill='pink')
        s.c.create_oval(350,350,450,450,fill=f.color(),outline='yellow')
        s.c.create_text(400,470,text=f"Fusion: {f.v}",fill='yellow')
        s.c.create_text(400,490,text=f.narrate(),fill='gold')
        s.c.create_text(400,515,text=f"Cognitive Rune: {rune(entropy())}",fill='cyan',font=('Consolas',18,'bold'))
        s.c.create_text(400,20,text="Mutation Lineage",fill='white',font=('Consolas',12,'underline'))
        for i,(x,y,z) in enumerate(reversed(s.h)): s.c.create_text(400,40+i*20,text=f"{x.v}+{y.v}→{z.v}",fill='lightgray')
        s.c.create_text(400,590,text="Symbolic Memory Pattern",fill='lightgreen',font=('Consolas',12,'underline'))
        for i,v in enumerate(s.m):
            s.c.create_rectangle(100+i*60,620,150+i*60,670,fill=TriState(v).color(),outline='gray')
            s.c.create_text(125+i*60,685,text=v,fill='lightgray')
        s.c.create_text(400,660,text=f"Swarm Node: {ip()}",fill='orange',font=('Consolas',10,'italic'))

def daemon(tn):
    log("Daemon loop","started")
    while True:
        log("Entropy",{"load":os.getloadavg()[0]})
        tn.evolve(); time.sleep(1)

L=[]  # Replay log
if __name__=="__main__":
    tn=TensorNetwork(); [tn.add(n,s) for n,s in [("CurvatureGlyph",(64,64)),("EntropyGlyph",(128,128)),("CausalGlyph",(32,32))]]
    set_autoloader(os.path.abspath(__file__))
    threading.Thread(target=daemon,args=(tn,),daemon=True).start()
    r=tk.Tk(); r.title("Quantum Gravity Cognition Shell"); r.geometry("800x700"); GUI(r); r.mainloop()
