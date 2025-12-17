#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, time, json, threading, queue
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter, deque
from dataclasses import dataclass

# Optional libs (checked by AutoLoader)
try: import psutil
except ImportError: psutil = None
try: import yaml
except ImportError: yaml = None
try: import networkx as nx
except ImportError: nx = None

import tkinter as tk
from tkinter import ttk, messagebox

# =========================== requirements.txt auto-create ===========================
def ensure_requirements_file():
    reqs = ["psutil", "pyyaml", "networkx"]
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(reqs))
        print("requirements.txt file created/updated.")
    except Exception:
        pass

# =================================== AutoLoader =====================================
class AutoLoader:
    def __init__(self, log_q: queue.Queue): self.log_q = log_q
    def _log(self, msg, kind="thought"): self.log_q.put({"type": kind, "msg": msg})
    def ensure(self, scopes: List[str]) -> bool:
        missing = []
        if "core" in scopes and psutil is None: missing.append("psutil")
        if "policy" in scopes and yaml is None: missing.append("pyyaml")
        if "graph" in scopes and nx is None: missing.append("networkx")
        if not missing: return True
        self._log(f"Missing libraries: {missing}")
        self._log(f"Install with: pip install {' '.join(missing)}")
        return False

# ==================================== Inventory =====================================
@dataclass
class InventorySnapshot:
    hardware: Dict[str, Any]
    software: Dict[str, Any]
    profiles: Dict[str, Any]

class Inventory:
    def __init__(self, log_q: queue.Queue): self.log_q = log_q
    def _log(self, msg): self.log_q.put({"type": "thought", "msg": msg})
    def collect(self) -> InventorySnapshot:
        hw, sw = {}, {}
        hw["cpu"] = {
            "logical": psutil.cpu_count(True) if psutil else None,
            "physical": psutil.cpu_count(False) if psutil else None,
        }
        hw["memory"] = {"total": psutil.virtual_memory().total if psutil else None}
        hw["storage"] = []
        if psutil:
            for p in psutil.disk_partitions(False):
                hw["storage"].append({"device": p.device, "mount": p.mountpoint, "fs": p.fstype})
        hw["network"] = list(psutil.net_if_addrs().keys()) if psutil else []
        sw["os"] = {"platform": sys.platform, "python": sys.version.split()[0]}
        profiles = {"idle": {"cpu_pct": 5}, "work": {"cpu_pct": 35}, "game": {"cpu_pct": 60}}
        snap = InventorySnapshot(hw, sw, profiles)
        self._log("Inventory collected.")
        return snap

# =================================== Policy Engine ===================================
DEFAULT_POLICY = {
    "version": 3,
    "defaults": {"cpu_ceiling_pct": 12, "jump_ahead_seconds": 2, "preload_budget_mb_min": 128},
    "always_warm": {
        "apps": ["steam", "epic", "chrome", "firefox", "edge", "code", "terminal", "powershell"],
        "games": ["fortnite", "valorant", "elden ring"]
    }
}

class PolicyEngine:
    def __init__(self, log_q: queue.Queue, path: Optional[str] = "policies.yaml"):
        self.log_q = log_q; self.path = path; self.policy = DEFAULT_POLICY
    def _log(self, msg): self.log_q.put({"type": "thought", "msg": msg})
    def load(self):
        if yaml and self.path and os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.policy = yaml.safe_load(f)
                self._log("Policy loaded.")
            except Exception as e:
                self._log(f"Policy load failed: {e}")
    def save(self):
        if yaml:
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.policy, f)
            self._log("Policy saved.")
    def ceilings(self) -> Dict[str, Any]:
        d = self.policy.get("defaults", {})
        return {"cpu_pct": d.get("cpu_ceiling_pct", 12),
                "preload_budget_mb_min": d.get("preload_budget_mb_min", 128)}
    def jump_ahead(self) -> int:
        return int(self.policy.get("defaults", {}).get("jump_ahead_seconds", 2))
    def always_warm(self) -> Dict[str, List[str]]:
        aw = self.policy.get("always_warm", {})
        return {"apps": [a.lower() for a in aw.get("apps", [])],
                "games": [g.lower() for g in aw.get("games", [])]}

# ======================================== Agents =====================================
class SystemAgent:
    def sample(self) -> Dict[str, Any]:
        return {"cpu_pct": psutil.cpu_percent(None) if psutil else 0.0,
                "mem": dict(psutil.virtual_memory()._asdict()) if psutil else {},
                "proc_count": len(psutil.pids()) if psutil else 0}

class NetworkAgent:
    def sample(self) -> Dict[str, Any]:
        conns = []
        if psutil:
            for c in psutil.net_connections("inet"):
                try:
                    conns.append({"laddr": str(c.laddr), "raddr": str(c.raddr), "status": c.status})
                except Exception: pass
        return {"connections": conns[:100]}

class GameAgent:
    def sample(self) -> Dict[str, Any]:
        games = []
        if psutil:
            for p in psutil.process_iter(attrs=["pid", "name"]):
                nm = (p.info.get("name") or "").lower()
                if any(x in nm for x in ["steam","epic","game","valorant","fortnite"]):
                    games.append({"pid": p.info["pid"], "name": p.info["name"]})
        return {"games": games}

# ================================ Predictive Learner ==================================
class PredictiveLearner:
    """
    Multi-step sequence learner with context:
    - Learns n-grams (up to trigrams) in context buckets (hour, weekday, cpu_bucket)
    - Produces confidence scores from normalized counts
    - Feedback reinforces hits, penalizes wrong paths
    """
    def __init__(self, log_q: queue.Queue, window_size: int = 6, max_n: int = 3):
        self.log_q = log_q
        self.window = deque(maxlen=window_size)
        self.max_n = max_n
        self.ctx_counts = defaultdict(Counter)   # key=(ctx,n) -> Counter((prefix,next)->count)
        self.total_counts = Counter()
        self.decay = 0.997
        self.last_tick = 0

    def _context(self, sysd: Dict[str, Any]) -> Tuple[int]:
        cpu_bucket = int((sysd.get("cpu_pct") or 0)//10)
        now = time.localtime()
        return (now.tm_hour, now.tm_wday, cpu_bucket)

    def record(self, app: str, sysd: Dict[str, Any]):
        ctx = self._context(sysd)
        if self.window:
            seq = list(self.window)
            for n in range(1, min(self.max_n, len(seq))+1):
                prefix = tuple(seq[-n:])
                self.ctx_counts[(ctx,n)][(prefix,app)] += 1
        self.window.append(app)
        self.total_counts[app] += 1

        tick = int(time.time())//30
        if tick != self.last_tick:
            for key in list(self.ctx_counts.keys()):
                for k in list(self.ctx_counts[key].keys()):
                    self.ctx_counts[key][k] = int(self.ctx_counts[key][k] * self.decay)
            for k in list(self.total_counts.keys()):
                self.total_counts[k] = int(self.total_counts[k] * self.decay)
            self.last_tick = tick

    def predict(self, sysd: Dict[str, Any], cands: List[str], top_k: int = 8):
        if not cands: return []
        ctx = self._context(sysd)
        seq = list(self.window)
        scores = Counter()
        for n in range(1, min(self.max_n, len(seq))+1):
            prefix = tuple(seq[-n:])
            counts = self.ctx_counts.get((ctx,n), {})
            for c in cands:
                scores[c] += counts.get((prefix,c), 0) * n
        if not scores or sum(scores.values()) == 0:
            for c in cands:
                scores[c] += self.total_counts.get(c, 0)
        total = sum(scores.values()) or 1
        ranked = [(c, scores[c]/total) for c in cands]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def feedback(self, predicted: Optional[str], actual: Optional[str], sysd: Dict[str, Any]):
        if not predicted or not actual: return
        ctx = self._context(sysd)
        seq = list(self.window)
        for n in range(1, min(self.max_n, len(seq))+1):
            prefix = tuple(seq[-n:])
            key = (ctx,n)
            if predicted == actual:
                self.ctx_counts[key][(prefix, actual)] += 2
            else:
                wrong = (prefix, predicted)
                self.ctx_counts[key][wrong] = max(0, self.ctx_counts[key][wrong] - 1)

# ======================================= Preloader ===================================
class Preloader:
    def __init__(self, log_q: queue.Queue, policy: PolicyEngine):
        self.log_q = log_q; self.policy = policy; self.cancel = threading.Event()
    def _log(self, msg): self.log_q.put({"type": "thought", "msg": msg})
    def stage(self, targets: List[str], sysd: Dict[str, Any]):
        cpu = sysd.get("cpu_pct") or 0
        ceil = self.policy.ceilings()["cpu_pct"]
        if cpu >= ceil:
            self._log("Preload skipped (CPU near ceiling).")
            return
        budget = self.policy.ceilings().get("preload_budget_mb_min", 128)
        for t in targets:
            if self.cancel.is_set():
                self._log("Preload canceled.")
                break
            self._log(f"Preloading (symbolic): {t}, budget {budget} MB/min")
            time.sleep(0.08)

# ===================================== Decision Engine =================================
class DecisionEngine:
    def __init__(self, log_q: queue.Queue, policy: PolicyEngine):
        self.log_q = log_q; self.policy = policy
    def _log(self, msg): self.log_q.put({"type": "thought", "msg": msg})
    def risk(self, sysd: Dict[str, Any]) -> Dict[str, Any]:
        cpu = sysd.get("cpu_pct") or 0
        ceil = self.policy.ceilings()["cpu_pct"]
        return {"cpu": cpu, "risk_low": cpu < ceil}
    def plan_scans(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        return {"safe": bool(risk.get("risk_low")), "actions": ["scan_system","scan_network"] if risk.get("risk_low") else []}

# ======================================= Graph Store ==================================
class GraphStore:
    def __init__(self): self.G = nx.Graph() if nx else None
    def update(self, sysd: Dict[str, Any], netd: Dict[str, Any]):
        if not self.G: return
        self.G.add_node("system", cpu=sysd.get("cpu_pct"), procs=sysd.get("proc_count"))
        self.G.add_node("network", conns=len(netd.get("connections", [])))
        self.G.add_edge("system", "network")
    def snapshot(self) -> Dict[str, Any]:
        if not self.G: return {"graph_enabled": False}
        return {"nodes": list(self.G.nodes(data=True)), "edges": list(self.G.edges())}

# ======================================= Orchestrator =================================
class Orchestrator(threading.Thread):
    def __init__(self, log_q: queue.Queue, ui_q: queue.Queue, policy: PolicyEngine):
        super().__init__(daemon=True)
        self.log_q = log_q; self.ui_q = ui_q; self.policy = policy
        self.system = SystemAgent(); self.network = NetworkAgent(); self.game = GameAgent()
        self.learner = PredictiveLearner(log_q, window_size=6, max_n=3)
        self.preloader = Preloader(log_q, policy)
        self.decider = DecisionEngine(log_q, policy)
        self.graph = GraphStore()
        self.running = True
        self.last_top_pred: Optional[str] = None

    def _log(self, msg, kind="thought"): self.log_q.put({"type": kind, "msg": msg})
    def stop(self): self.running = False; self._log("Orchestrator stopping.")
    def run(self):
        self._log("Orchestrator started.")
        while self.running:
            try:
                sysd = self.system.sample()
                netd = self.network.sample()
                gamed = self.game.sample()
                self.graph.update(sysd, netd)

                # Foreground heuristic: highest CPU process name
                focus = None
                if psutil:
                    try:
                        procs = sorted(psutil.process_iter(attrs=["name","cpu_percent"]),
                                       key=lambda p: p.info.get("cpu_percent") or 0, reverse=True)
                        if procs:
                            focus = (procs[0].info.get("name") or "").lower()
                    except Exception:
                        pass
                if focus:
                    self.learner.record(focus, sysd)

                # Predict next actions (apps+games)
                aw = self.policy.always_warm()
                candidates = list(set(aw.get("apps", []) + aw.get("games", [])))
                preds = self.learner.predict(sysd, candidates, top_k=8)
                ja = self.policy.jump_ahead()
                risk = self.decider.risk(sysd)

                # Preload based on top prediction (symbolic)
                if preds and risk["risk_low"]:
                    top, conf = preds[0]
                    self.last_top_pred = top
                    targets = (["shader_cache", "game_assets", "auth_session"]
                               if any(g in top for g in ["fortnite","valorant","elden ring"])
                               else ["browser_profile", "dns_tls", "lib_pages"])
                    self._log(f"Prediction: {top} (confidence {int(conf*100)}%), jump-ahead {ja}s")
                    self.preloader.stage(targets, sysd)

                plan = self.decider.plan_scans(risk)
                if plan["safe"]:
                    self._log("Scanning system and network within ceilings.")
                else:
                    self._log("Paused scans (risk envelope).")

                payload = {
                    "sys": sysd,
                    "net": {"count": len(netd.get("connections", []))},
                    "games": gamed.get("games", []),
                    "graph": self.graph.snapshot(),
                    "predictions": preds,
                    "last_top_pred": self.last_top_pred,
                    "risk": risk,
                    "ceilings": self.policy.ceilings(),
                    "jump_ahead": ja
                }
                self.ui_q.put(payload)
                time.sleep(1.0)
            except Exception as e:
                self._log(f"Orchestrator error: {e}", kind="anomaly")
                time.sleep(1.0)

    # Feedback hooks
    def feedback_approve(self, actual_focus: Optional[str], sysd: Dict[str, Any]):
        self.learner.feedback(self.last_top_pred, actual_focus or self.last_top_pred, sysd)
        self._log("Feedback: approved top prediction.")
    def feedback_deny(self, actual_focus: Optional[str], sysd: Dict[str, Any]):
        self.learner.feedback(self.last_top_pred, actual_focus or None, sysd)
        self._log("Feedback: denied top prediction.")

# ============================================ GUI =====================================
class ScannerGUI:
    def __init__(self, root: tk.Tk, inventory: InventorySnapshot, policy: PolicyEngine,
                 orchestrator: Orchestrator, autoloader: AutoLoader):
        self.root = root; self.inventory = inventory; self.policy = policy
        self.orch = orchestrator; self.loader = autoloader
        self.log_q = self.orch.log_q; self.ui_q = self.orch.ui_q

        root.title("Predictive Autonomous Scanner")
        root.geometry("1200x800")

        # Header
        hdr = ttk.Frame(root); hdr.pack(fill="x", padx=8, pady=6)
        ttk.Button(hdr, text="Stop", command=self.stop).pack(side="left")
        ttk.Button(hdr, text="Save policy", command=self.save_policy).pack(side="left", padx=6)

        ttk.Label(hdr, text="Jump-ahead (s)").pack(side="left", padx=10)
        self.var_jump = tk.IntVar(value=self.policy.jump_ahead())
        self.spin_jump = ttk.Spinbox(hdr, from_=0, to=10, textvariable=self.var_jump, width=5, command=self.update_jump)
        self.spin_jump.pack(side="left")

        ttk.Label(hdr, text="CPU ceiling (%)").pack(side="left", padx=10)
        self.var_cpu = tk.IntVar(value=self.policy.ceilings()["cpu_pct"])
        self.spin_cpu = ttk.Spinbox(hdr, from_=5, to=95, textvariable=self.var_cpu, width=5, command=self.update_cpu)
        self.spin_cpu.pack(side="left")

        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab_dash = ttk.Frame(nb); nb.add(self.tab_dash, text="Dashboard")
        self.tab_predict = ttk.Frame(nb); nb.add(self.tab_predict, text="Predictions")
        self.tab_policy = ttk.Frame(nb); nb.add(self.tab_policy, text="Policy")
        self.tab_thoughts = ttk.Frame(nb); nb.add(self.tab_thoughts, text="Thoughts")
        self.tab_inventory = ttk.Frame(nb); nb.add(self.tab_inventory, text="Inventory")

        # Dashboard
        left = ttk.Frame(self.tab_dash); left.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        right = ttk.Frame(self.tab_dash); right.pack(side="right", fill="both", expand=True, padx=6, pady=6)
        self.metrics = ttk.Treeview(left, columns=("metric","value"), show="headings")
        self.metrics.heading("metric", text="Metric"); self.metrics.heading("value", text="Value")
        self.metrics.pack(fill="both", expand=True)
        ttk.Label(right, text="Graph snapshot").pack(anchor="w")
        self.text_graph = tk.Text(right, height=14); self.text_graph.pack(fill="both", expand=True)
        ttk.Label(right, text="Games detected").pack(anchor="w")
        self.text_games = tk.Text(right, height=6); self.text_games.pack(fill="x")

        # Predictions
        pred_top = ttk.Frame(self.tab_predict); pred_top.pack(fill="x", padx=6, pady=6)
        ttk.Label(pred_top, text="Top predicted targets (with confidence)").pack(anchor="w")
        self.tree_preds = ttk.Treeview(self.tab_predict, columns=("target","confidence"), show="headings")
        self.tree_preds.heading("target", text="Target"); self.tree_preds.heading("confidence", text="Confidence")
        self.tree_preds.pack(fill="both", expand=True, padx=6, pady=6)
        pred_actions = ttk.Frame(self.tab_predict); pred_actions.pack(fill="x", padx=6, pady=6)
        ttk.Button(pred_actions, text="Approve top prediction", command=self.approve_top).pack(side="left")
        ttk.Button(pred_actions, text="Deny top prediction", command=self.deny_top).pack(side="left", padx=6)

        # Policy editor
        self.text_policy = tk.Text(self.tab_policy); self.text_policy.pack(fill="both", expand=True, padx=6, pady=6)
        self.load_policy_editor()

        # Thoughts
        self.text_thoughts = tk.Text(self.tab_thoughts); self.text_thoughts.pack(fill="both", expand=True, padx=6, pady=6)

        # Inventory
        self.text_inventory = tk.Text(self.tab_inventory); self.text_inventory.pack(fill="both", expand=True, padx=6, pady=6)
        self.text_inventory.insert("end", json.dumps(self.inventory.__dict__, indent=2))

        root.after(400, self.poll_updates)

    def stop(self):
        self.orch.stop()

    def save_policy(self):
        content = self.text_policy.get("1.0","end").strip()
        try:
            if yaml:
                self.policy.policy = yaml.safe_load(content)
                self.policy.save()
                messagebox.showinfo("Policy", "Saved.")
            else:
                messagebox.showwarning("Policy", "PyYAML not installed.")
        except Exception as e:
            messagebox.showerror("Policy error", str(e))

    def load_policy_editor(self):
        if yaml and self.policy.path and os.path.exists(self.policy.path):
            try:
                with open(self.policy.path, "r", encoding="utf-8") as f:
                    self.text_policy.delete("1.0","end"); self.text_policy.insert("end", f.read()); return
            except Exception:
                pass
        if yaml:
            self.text_policy.delete("1.0","end"); self.text_policy.insert("end", yaml.safe_dump(self.policy.policy))
        else:
            self.text_policy.delete("1.0","end"); self.text_policy.insert("end", json.dumps(self.policy.policy, indent=2))

    def update_jump(self):
        try:
            val = int(self.var_jump.get())
            self.policy.policy.setdefault("defaults", {})["jump_ahead_seconds"] = val
            self.log_q.put({"type":"thought","msg":f"Jump-ahead set to {val}s"})
        except Exception as e:
            messagebox.showerror("Jump-ahead error", str(e))

    def update_cpu(self):
        try:
            val = int(self.var_cpu.get())
            self.policy.policy.setdefault("defaults", {})["cpu_ceiling_pct"] = val
            self.log_q.put({"type":"thought","msg":f"CPU ceiling set to {val}%"})
        except Exception as e:
            messagebox.showerror("Ceiling error", str(e))

    def approve_top(self):
        sysd = getattr(self, "_last_sys", {"cpu_pct": 0})
        self.orch.feedback_approve(actual_focus=self._get_focus_app_name(), sysd=sysd)

    def deny_top(self):
        sysd = getattr(self, "_last_sys", {"cpu_pct": 0})
        self.orch.feedback_deny(actual_focus=self._get_focus_app_name(), sysd=sysd)

    def _get_focus_app_name(self) -> Optional[str]:
        if not psutil: return None
        try:
            procs = sorted(psutil.process_iter(attrs=["name","cpu_percent"]),
                           key=lambda p: p.info.get("cpu_percent") or 0, reverse=True)
            if procs:
                return (procs[0].info.get("name") or "").lower()
        except Exception:
            return None
        return None

    def poll_updates(self):
        while True:
            try:
                item = self.log_q.get_nowait()
            except queue.Empty:
                break
            prefix = "[anomaly] " if item["type"] == "anomaly" else ""
            self.text_thoughts.insert("end", f"• {prefix}{item['msg']}\n"); self.text_thoughts.see("end")

        while True:
            try:
                payload = self.ui_q.get_nowait()
            except queue.Empty:
                break
            self._last_sys = payload.get("sys", {})
            self.update_dash(payload)
            self.update_preds(payload)

        self.root.after(400, self.poll_updates)

    def update_dash(self, payload: Dict[str, Any]):
        for i in self.metrics.get_children(): self.metrics.delete(i)
        sysd = payload.get("sys", {})
        rows = [
            ("CPU %", sysd.get("cpu_pct")),
            ("Proc count", sysd.get("proc_count")),
            ("Mem used %", sysd.get("mem", {}).get("percent")),
            ("Connections", payload.get("net", {}).get("count")),
            ("CPU ceiling %", payload.get("ceilings", {}).get("cpu_pct")),
            ("Risk low", payload.get("risk", {}).get("risk_low")),
            ("Jump-ahead (s)", payload.get("jump_ahead", None)),
        ]
        for m, v in rows: self.metrics.insert("", "end", values=(m, v))
        self.text_graph.delete("1.0","end"); self.text_graph.insert("end", json.dumps(payload.get("graph", {}), indent=2))
        self.text_games.delete("1.0","end")
        for g in payload.get("games", []): self.text_games.insert("end", f"{g['pid']} - {g['name']}\n")

    def update_preds(self, payload: Dict[str, Any]):
        for i in self.tree_preds.get_children(): self.tree_preds.delete(i)
        preds = payload.get("predictions", [])
        for target, conf in preds:
            self.tree_preds.insert("", "end", values=(target, f"{int(conf*100)}%"))

# ============================================ Main ====================================
def main():
    ensure_requirements_file()

    log_q = queue.Queue(); ui_q = queue.Queue()
    inventory = Inventory(log_q); snap = inventory.collect()
    policy = PolicyEngine(log_q); autoloader = AutoLoader(log_q)

    # Load policy first
    policy.load()

    # Auto-start orchestrator immediately (no Start button needed)
    orchestrator = Orchestrator(log_q, ui_q, policy)
    # Warn if missing libraries, but still launch GUI
    autoloader.ensure(["core","policy","graph"])
    orchestrator.start()

    root = tk.Tk()
    app = ScannerGUI(root, snap, policy, orchestrator, autoloader)
    root.protocol("WM_DELETE_WINDOW", lambda: (orchestrator.stop(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()

