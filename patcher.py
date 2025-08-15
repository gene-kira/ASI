import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import queue

# ---------- CONFIG ----------
API_BASE = "http://localhost:9000"   # Decision‑Plane endpoint
MAGIC_BG  = "#2b003e"                # dark purple
MAGIC_FG  = "#ffcc00"                # gold
WINDOW_W, WINDOW_H = 600, 400

# ---------- THREAD HELPERS ----------
def fetch_patches(q):
    """Background thread that polls the AI layer for available patches."""
    while True:
        try:
            r = requests.get(f"{API_BASE}/patches")
            if r.ok:
                q.put(r.json())   # list of patch dicts
        except Exception as e:
            print("poll error:", e)
        time.sleep(5)

def deploy_patch(patch_id, host, result_q):
    """Background thread that calls the Decision‑Plane /deploy endpoint."""
    try:
        r = requests.post(
            f"{API_BASE}/deploy",
            json={"patchId": patch_id, "host": host}
        )
        if r.ok:
            result_q.put({"id": patch_id, "status": "ok", "output": r.json().get("output")})
        else:
            result_q.put({"id": patch_id, "status": "fail", "error": r.text})
    except Exception as e:
        result_q.put({"id": patch_id, "status": "fail", "error": str(e)})

# ---------- GUI ----------
class MagicBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MagicBox – One‑Click Patch Deploy")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.configure(bg=MAGIC_BG)

        # Queue for patch list updates
        self.patch_queue = queue.Queue()
        threading.Thread(target=fetch_patches, daemon=True).start()

        # Frame to hold patches
        self.frame = ttk.Frame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            self.frame,
            columns=("Title", "Host"),
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("Title", text="Patch Title")
        self.tree.heading("Host",  text="Target Host")
        self.tree.pack(fill="both", expand=True)

        # Deploy button
        self.deploy_btn = ttk.Button(
            self,
            text="🟢 Deploy Selected Patch",
            command=self.on_deploy_click
        )
        self.deploy_btn.pack(pady=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var)
        self.status_bar.pack(side="bottom", fill="x")

        # Result queue for deployment feedback
        self.result_queue = queue.Queue()
        self.after(100, self.check_queues)

    def on_deploy_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please pick a patch to deploy.")
            return

        item = self.tree.item(selected[0])
        patch_id = item["values"][2]   # we store id as hidden third column
        host     = item["values"][3]

        self.status_var.set(f"Deploying {item['values'][0]} …")
        threading.Thread(
            target=deploy_patch,
            args=(patch_id, host, self.result_queue),
            daemon=True
        ).start()

    def check_queues(self):
        # Update patch list if new data is available
        try:
            patches = self.patch_queue.get_nowait()
            self.refresh_tree(patches)
        except queue.Empty:
            pass

        # Handle deployment results
        try:
            res = self.result_queue.get_nowait()
            if res["status"] == "ok":
                messagebox.showinfo("Success", f"Patch {res['id']} deployed.\n\n{res['output']}")
                self.status_var.set("Deployed successfully")
            else:
                messagebox.showerror("Failure", f"Patch {res['id']} failed:\n{res.get('error', 'Unknown error')}")
                self.status_var.set("Deployment failed")
        except queue.Empty:
            pass

        self.after(200, self.check_queues)

    def refresh_tree(self, patches):
        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Insert new ones
        for p in patches:
            # Hidden columns: id and host for internal use
            self.tree.insert(
                "",
                "end",
                values=(p["title"], p["host"], p["id"], p["host"]),
                tags=("patch",),
            )
        # Hide the last two columns (id, host) from view
        self.tree.column("#3", width=0, stretch=False)
        self.tree.column("#4", width=0, stretch=False)

if __name__ == "__main__":
    app = MagicBox()
    app.mainloop()