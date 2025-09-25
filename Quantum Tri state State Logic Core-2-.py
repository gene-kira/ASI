import tkinter as tk, psutil, threading, time, socket, os, sys, subprocess
for p in ['numba','numpy','pynvml']: exec(f"import {p}") if p in sys.modules else subprocess.run([sys.executable,'-m','pip','install',p])
from numba import cuda; import numpy as np; from pynvml import *

class TriState:
    def __init__(s,v): assert v in ['0','1','Ø']; s.v=v
    def mutate(s,o): return TriState('Ø' if 'Ø' in [s.v,o.v] or s.v!=o.v else s.v)
    def color(s): return {'0':'black','1':'white','Ø':'purple'}[s.v]
    def narrate(s): return {'0':'Void detected.','1':'Signal active.','Ø':'Fusion achieved.'}[s.v]

@cuda.jit
def fuse_kernel(a,b,r): i=cuda.threadIdx.x+cuda.blockIdx.x*cuda.blockDim.x; 
if i<a.size: r[i]=2 if 2 in [a[i],b[i]] or a[i]!=b[i] else a[i]

def gpu_fuse(a,b):
    a,b=np.array(a,np.int32),np.array(b,np.int32)
    r=cuda.device_array_like(a)
    fuse_kernel[(len(a)+31)//32,32](cuda.to_device(a),cuda.to_device(b),r)
    return r.copy_to_host()

def entropy(): return (psutil.cpu_percent(1)+psutil.virtual_memory().percent)/200
def vram(): nvmlInit(); h=nvmlDeviceGetHandleByIndex(0); i=nvmlDeviceGetMemoryInfo(h); nvmlShutdown(); return i.used/i.total
def purge(): open("borg_temp.txt","w").write("█"*1024); os.remove("borg_temp.txt")
def ip(): return socket.gethostbyname(socket.gethostname())

def pattern(): e=vram(); return ['0' if e<.33 else '1' if e<.66 else 'Ø']*8
def rune(e): return 'Ψ' if e<.33 else 'Δ' if e<.66 else '∞'

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

if __name__=="__main__":
    r=tk.Tk(); r.title("Borg Assimilation — GPU Shell"); r.geometry("800x700"); GUI(r); r.mainloop()
