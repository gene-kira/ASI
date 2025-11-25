# === AUTO-ELEVATION CHECK ===
import os, sys, ctypes

def ensure_admin():
    """ Relaunch the script with admin rights if not already elevated. """
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            print("[ASI Console] Elevation required. Relaunching as administrator...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit()
    except Exception as e:
        print(f"[ASI Console] Elevation failed: {e}")
        sys.exit()

ensure_admin()

# === MAIN CONSOLE ===
import json, time, threading, subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Core Settings ---
FOLDER = r"C:\ProgramData\ASUS\QCNF"
TARGET = "ManualRead.bin"
CONFIG = "asi_config.json"

auto_kill, safe_mode = False, False
current_profile, selected_service = CONFIG, None
RELOCATE_TARGET = None  # will be chosen interactively

# --- Config ---
def load_config(path=CONFIG):
    global auto_kill, safe_mode, selected_service, current_profile
    if os.path.exists(path):
        try:
            with open(path) as f: cfg=json.load(f)
            auto_kill, safe_mode = cfg.get("auto_kill",False), cfg.get("safe_mode",False)
            selected_service, current_profile = cfg.get("service"), path
            root.after(0, update_status_bar)
            log(f"[ASI] Profile loaded: {os.path.basename(path)}")
        except Exception as e: log(f"[ERROR] Config load failed: {e}")

def save_config(path=CONFIG):
    cfg={"auto_kill":auto_kill,"safe_mode":safe_mode,"service":service_var.get()}
    try:
        with open(path,"w") as f: json.dump(cfg,f,indent=2)
        current_profile=path; root.after(0, update_status_bar)
        log(f"[ASI] Profile saved: {os.path.basename(path)}")
    except Exception as e: log(f"[ERROR] Config save failed: {e}")

# --- Service Control ---
def list_services():
    try:
        out=subprocess.run(["sc","query","state=","all"],capture_output=True,text=True).stdout
        return [line.split(":")[1].strip() for line in out.splitlines() if "SERVICE_NAME" in line and ("ASUS" in line.upper() or "QCNF" in line.upper())]
    except: return []

def service_status(name):
    try:
        out=subprocess.run(["sc","query",name],capture_output=True,text=True).stdout
        return "Running" if "RUNNING" in out else "Stopped" if "STOPPED" in out else "Unknown"
    except: return "Not Found"

def disable_service(name):
    log(f"[ASI] Disabling {name}")
    subprocess.run(["sc","stop",name],check=False)
    subprocess.run(["sc","config",name,"start=","disabled"],check=False)
    root.after(0, update_status); save_config()

def enable_service(name):
    log(f"[ASI] Enabling {name}")
    subprocess.run(["sc","config",name,"start=","auto"],check=False)
    subprocess.run(["sc","start",name],check=False)
    root.after(0, update_status); save_config()

def update_status(*a):
    if service_var.get():
        status_label.config(text=f"Status: {service_status(service_var.get())}")

# --- Refactored Monitor Handler ---
class Handler(FileSystemEventHandler):
    def on_created(self,e):
        if e.src_path.endswith(TARGET):
            log(f"[ASI] {TARGET} created")
            if auto_kill and service_var.get():
                root.after(0, lambda: disable_service(service_var.get()))
                root.after(0, lambda: self.relocate_file(e.src_path))
            elif safe_mode and service_var.get():
                log("[ASI] Safe Mode: awaiting confirmation...")
                root.after(0, lambda: self.prompt(e.src_path))

    def prompt(self, path):
        if service_var.get():
            if messagebox.askyesno("Safe Mode", f"{TARGET} detected.\nDisable {service_var.get()} and relocate file?"):
                disable_service(service_var.get())
                self.relocate_file(path)

    def on_deleted(self,e):
        if e.src_path.endswith(TARGET):
            log(f"[ASI] {TARGET} deleted")

    def relocate_file(self, path):
        try:
            global RELOCATE_TARGET
            if not RELOCATE_TARGET:
                log("[ERROR] No relocation target selected")
                return
            os.makedirs(os.path.dirname(RELOCATE_TARGET), exist_ok=True)
            with open(RELOCATE_TARGET, "w") as f:
                f.write("")
            if os.path.exists(path):
                os.remove(path)
            subprocess.run(f'mklink "{path}" "{RELOCATE_TARGET}"', shell=True)
            log(f"[⚡ FILE RELOCATED ⚡] {TARGET} redirected to {RELOCATE_TARGET}")
        except Exception as ex:
            log(f"[ERROR] Failed to relocate {TARGET}: {ex}")

def start_monitor():
    obs=Observer(); obs.schedule(Handler(),FOLDER,recursive=False); obs.start()
    threading.Thread(target=lambda: obs.join(),daemon=True).start()

# --- Logging ---
def log(msg): log_box.insert(tk.END,time.strftime("%H:%M:%S")+" "+msg+"\n"); log_box.see(tk.END)

# --- GUI ---
root=tk.Tk(); root.title("ASI Oversight Console"); root.geometry("700x500"); root.configure(bg="black")
style={"bg":"black","fg":"lime","font":("Consolas",10)}

tk.Label(root,text="Select Service:",**style).pack(pady=5)
services=list_services(); service_var=tk.StringVar(); service_var.trace("w",update_status)
ttk.Combobox(root,textvariable=service_var,values=services,state="readonly").pack(pady=5)

status_label=tk.Label(root,text="Status: --",**style); status_label.pack(pady=5)

tk.Button(root,text="Disable",command=lambda:disable_service(service_var.get()),bg="red",fg="white").pack(pady=5)
tk.Button(root,text="Enable",command=lambda:enable_service(service_var.get()),bg="green",fg="white").pack(pady=5)

def toggle_auto(): 
    global auto_kill,safe_mode; auto_kill=not auto_kill; safe_mode=False
    auto_btn.config(text=f"Auto-Kill: {'ON' if auto_kill else 'OFF'}"); save_config()
def toggle_safe(): 
    global safe_mode,auto_kill; safe_mode=not safe_mode; auto_kill=False
    safe_btn.config(text=f"Safe Mode: {'ON' if safe_mode else 'OFF'}"); save_config()

auto_btn=tk.Button(root,text="Auto-Kill: OFF",command=toggle_auto,bg="orange",fg="black"); auto_btn.pack(pady=5)
safe_btn=tk.Button(root,text="Safe Mode: OFF",command=toggle_safe,bg="blue",fg="white"); safe_btn.pack(pady=5)

# --- Interactive relocation picker ---
def choose_relocate_target():
    global RELOCATE_TARGET
    folder = filedialog.askdirectory(title="Select relocation folder or network share")
    if folder:
        RELOCATE_TARGET = os.path.join(folder, TARGET)
        log(f"[ASI] Relocation target set to {RELOCATE_TARGET}")
    else:
        log("[ERROR] No relocation folder selected")

tk.Button(root,text="Choose Relocation Folder",command=choose_relocate_target,**style).pack(pady=5)

tk.Button(root,text="Save Profile",command=lambda:save_config(filedialog.asksaveasfilename(defaultextension=".json")),**style).pack(pady=5)
tk.Button(root,text="Load Profile",command=lambda:load_config(filedialog.askopenfilename(filetypes=[("JSON","*.json")])),**style).pack(pady=5)

log_box=tk.Text(root,height=12,width=80,bg="black",fg="lime",font=("Consolas",9)); log_box.pack(pady=5)

status_bar=tk.Label(root,text=f"Profile: {os.path.basename(current_profile)}",bd=1,relief=tk.SUNKEN,anchor="w",**style)
status_bar.pack(side=tk.BOTTOM,fill=tk.X)
def update_status_bar(): status_bar.config(text=f"Profile: {os.path.basename(current_profile)}")

# --- Init ---
load_config()
if selected_service and selected_service in services: service_var.set(selected_service)
if auto_kill: auto_btn.config(text="Auto-Kill: ON")
if safe_mode: safe_btn.config(text="Safe Mode: ON")

start_monitor()
root.mainloop()

