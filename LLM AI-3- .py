import importlib, subprocess, sys, os, json, time, re, logging, threading
from datetime import datetime
from typing import Dict, Any, Optional, List
import queue

# GUI
import tkinter as tk
from tkinter import ttk, scrolledtext

# ---------------------------
# Auto loader
# ---------------------------
def auto_import(package, import_name=None, extras=None):
    try:
        return importlib.import_module(import_name or package)
    except ImportError:
        logging.warning(f"Installing missing package: {package}{'['+extras+']' if extras else ''}")
        cmd = [sys.executable, "-m", "pip", "install", f"{package}[{extras}]" if extras else package]
        subprocess.check_call(cmd)
        return importlib.import_module(import_name or package)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

psutil = auto_import("psutil")
transformers = None
torch = None

# ---------------------------
# Model adapters (Transformers)
# ---------------------------
class BaseLLMAdapter:
    def __init__(self, name): self.name = name
    def generate(self, prompt, max_new_tokens=1200, temperature=0.35): raise NotImplementedError
    def score(self, text: str) -> float:
        if not text or text.startswith("ERROR"): return 0.0
        length = len(text)
        has_json = bool(re.search(r"\{.*\}", text, flags=re.S))
        py_blocks = len(re.findall(r"```python", text))
        steps = len(re.findall(r"^\s*\d+\.", text, flags=re.M))
        return (
            0.4 * min(length / 4000, 1.0) +
            0.3 * (1.0 if has_json else 0.0) +
            0.2 * min(py_blocks, 3) / 3 +
            0.1 * min(steps, 10) / 10
        )

class TransformersAdapter(BaseLLMAdapter):
    def __init__(self, name, device="cpu"):
        global transformers, torch
        transformers = transformers or auto_import("transformers")
        torch = torch or auto_import("torch")
        super().__init__(name)
        logging.info(f"Loading Transformers model: {name}")
        self.tok = transformers.AutoTokenizer.from_pretrained(name)
        self.model = transformers.AutoModelForCausalLM.from_pretrained(name)
        self.device = device
        try:
            self.model.to(device)
        except Exception as e:
            logging.warning(f"Device move failed, using CPU: {e}")

    def generate(self, prompt, max_new_tokens=1200, temperature=0.35):
        inputs = self.tok(prompt, return_tensors="pt").to(self.device)
        out = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tok.eos_token_id
        )
        return self.tok.decode(out[0], skip_special_tokens=True)

# ---------------------------
# Ensemble engine
# ---------------------------
class EnsembleEngine:
    def __init__(self, adapters: Dict[str, BaseLLMAdapter]):
        self.adapters = adapters
        self.modes = ["router", "blend"]
        self.default_max_new_tokens = 1200
        self.default_temperature = 0.35
        self.last_outputs: Dict[str, str] = {}

    def query_all(self, prompt, max_new_tokens=None, temperature=None, stop_event: Optional[threading.Event]=None):
        results = {}
        threads = []
        max_new_tokens = max_new_tokens or self.default_max_new_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        def run_one(name, adapter):
            if stop_event and stop_event.is_set(): return
            try:
                text = adapter.generate(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
                results[name] = text
                self.last_outputs[name] = text
            except Exception as e:
                results[name] = f"ERROR: {e}"

        for name, adapter in self.adapters.items():
            t = threading.Thread(target=run_one, args=(name, adapter), daemon=True)
            threads.append(t); t.start()

        for t in threads: t.join()
        return results

    def route_best(self, outputs):
        best_name, best_score = None, -1
        for name, text in outputs.items():
            sc = self.adapters[name].score(text)
            if sc > best_score:
                best_name, best_score = name, sc
        return best_name, outputs.get(best_name, "")

    def blend(self, outputs):
        # Merge Python code blocks and first-paragraph summaries
        codes = []
        summaries = []
        for name, text in outputs.items():
            if text.startswith("ERROR"): continue
            summaries.append(f"[{name}] {text.strip().split('\n\n')[0][:600]}")
            codes += re.findall(r"```python(.*?)```", text, flags=re.S)
        merged = []
        if summaries:
            merged.append("Unified summary:\n" + "\n".join(summaries[:6]))
        if codes:
            # de-duplicate
            seen = set(); uniq = []
            for c in codes:
                key = re.sub(r"\s+", " ", c.strip()).lower()
                if key not in seen:
                    seen.add(key); uniq.append(f"```python{c}```")
            merged.append("\nUnified Python blocks:\n" + "\n\n".join(uniq))
        return "\n".join(merged) if merged else "No actionable Python content to blend."

    def aggregate(self, mode, prompt, max_new_tokens=None, temperature=None, stop_event=None):
        outputs = self.query_all(prompt, max_new_tokens, temperature, stop_event)
        if mode == "router":
            _, best = self.route_best(outputs)
            return best, outputs
        if mode == "blend":
            return self.blend(outputs), outputs
        return "Unknown mode.", outputs

# ---------------------------
# Telemetry collection
# ---------------------------
def collect_telemetry(sample_secs=0.3) -> Dict[str, Any]:
    cpu = psutil.cpu_percent(interval=sample_secs)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()
    procs = []
    for p in psutil.process_iter(attrs=["pid","name","cpu_percent","memory_info","io_counters","num_threads"]):
        try:
            i = p.info
            procs.append({
                "pid": i["pid"], "name": i["name"], "cpu": i["cpu_percent"],
                "rss_mb": round((i["memory_info"].rss if i["memory_info"] else 0)/(1024*1024),2),
                "threads": i.get("num_threads"),
                "read_mb": round((i["io_counters"].read_bytes if i["io_counters"] else 0)/(1024*1024),2),
                "write_mb": round((i["io_counters"].write_bytes if i["io_counters"] else 0)/(1024*1024),2),
            })
        except Exception:
            pass
    procs_sorted = sorted(procs, key=lambda x: (x["cpu"] or 0, x["rss_mb"] or 0), reverse=True)[:12]
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": round(mem.used/(1024*1024),2),
        "swap_percent": swap.percent,
        "disk_percent": disk.percent,
        "disk_read_mb": round(disk_io.read_bytes/(1024*1024),2),
        "disk_write_mb": round(disk_io.write_bytes/(1024*1024),2),
        "net_bytes_sent": net_io.bytes_sent,
        "net_bytes_recv": net_io.bytes_recv,
        "top_processes": procs_sorted
    }

# ---------------------------
# Bottleneck analyzer
# ---------------------------
def analyze_bottlenecks(t: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    def add(kind, severity, detail): issues.append({"kind": kind, "severity": severity, "detail": detail})
    if (t["cpu_percent"] or 0) > 85: add("cpu_saturation", "high", f"CPU {t['cpu_percent']}%")
    if (t["memory_percent"] or 0) > 80: add("memory_pressure", "high", f"Mem {t['memory_percent']}% ({t['memory_used_mb']} MB)")
    if (t["swap_percent"] or 0) > 25: add("swap_activity", "medium", f"Swap {t['swap_percent']}%")
    if (t["disk_percent"] or 0) > 85: add("disk_capacity", "medium", f"Disk {t['disk_percent']}%")
    if (t["disk_read_mb"] + t["disk_write_mb"]) > 500: add("disk_io_heavy", "medium", f"IO {t['disk_read_mb']+t['disk_write_mb']} MB")
    for p in t["top_processes"][:6]:
        if (p["cpu"] or 0) > 60: add("process_cpu_hot", "medium", f"{p['name']}({p['pid']}) CPU {p['cpu']}%")
        if (p["rss_mb"] or 0) > 1500: add("process_mem_heavy", "medium", f"{p['name']}({p['pid']}) RSS {p['rss_mb']} MB")
        if (p["write_mb"] or 0) > 200 or (p["read_mb"] or 0) > 200:
            add("process_io_heavy", "low", f"{p['name']} IO R{p['read_mb']}MB/W{p['write_mb']}MB")
    score = min(100,
        (60 if any(i["severity"]=="high" for i in issues) else 0) +
        5 * sum(1 for i in issues if i["severity"]=="medium") +
        2 * sum(1 for i in issues if i["severity"]=="low")
    )
    return {"issues": issues, "bottleneck_score": score}

# ---------------------------
# Planner prompt (Python-only)
# ---------------------------
PLAN_SCHEMA = {
    "required": ["confidence", "summary", "program", "tasks"],
    "tasks_required": ["id","intent","lang","code","dry_run","risk"]
}

def build_prompt(telemetry: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    return f"""
You are an autonomous systems optimizer. Based on telemetry and bottleneck analysis, propose a NEW program to improve performance.
Return ONLY JSON with these keys:
- confidence (0..1), summary (string),
- program (string): name/purpose of the new optimization program,
- tasks (list): items with id, intent, lang, code, dry_run, risk, notes(optional).

Constraints:
- All tasks MUST have lang="python" and code MUST be valid Python.
- Prefer safe, reversible actions and mark risky tasks dry_run=true.
- Include performance-oriented actions: cleanups, log rotation, caching, concurrency tuning (advice via Python), and IO/network pacing (analysis scripts).
- Make tasks idempotent and observable (print what changed).

telemetry:
{json.dumps(telemetry, indent=2)}

analysis:
{json.dumps(analysis, indent=2)}
"""

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m: return None
    raw = m.group(0)
    try: return json.loads(raw)
    except Exception:
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        cleaned = re.sub(r"(\w+):", r'"\1":', cleaned)
        try: return json.loads(cleaned)
        except Exception: return None

def validate_plan(plan: Dict[str, Any]) -> bool:
    if not plan: return False
    for k in PLAN_SCHEMA["required"]:
        if k not in plan: return False
    if not isinstance(plan.get("tasks"), list): return False
    for t in plan["tasks"]:
        for req in PLAN_SCHEMA["tasks_required"]:
            if req not in t: return False
        if t["lang"] != "python": return False
        if t["risk"] not in ["low","medium","high"]: return False
        if not isinstance(t["code"], str) or not t["code"].strip(): return False
    return True

# ---------------------------
# Safe Python executor
# ---------------------------
ALLOWED_ENVS = {
    "print": print, "range": range, "len": len, "min": min, "max": max, "sum": sum,
    "json": json, "time": time,  # safe utilities
}

def execute_task(task: Dict[str, Any], dry_run_default=True) -> Dict[str, Any]:
    code = task["code"]
    dry_run = task.get("dry_run", dry_run_default)
    result = {"id": task["id"], "status": "skipped", "error": None}
    try:
        if dry_run:
            result["status"] = "dry_run"
            return result
        sandbox_globals = {"__builtins__": ALLOWED_ENVS}
        exec(code, sandbox_globals, {})
        result["status"] = "executed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result

# ---------------------------
# Backend service
# ---------------------------
class OptimizerBackend:
    def __init__(self, engine: EnsembleEngine, work_dir="optimizer_runs", interval=75):
        self.engine = engine
        self.work_dir = work_dir
        self.interval = interval
        self.stop_event = threading.Event()
        self.mode = "router"
        self.last_summary: Dict[str, Any] = {}
        self.last_plan: Optional[Dict[str, Any]] = None
        self.last_outputs: Dict[str, str] = {}
        self.last_aggregated: str = ""
        self.log_queue: "queue.Queue[str]" = queue.Queue()
        os.makedirs(work_dir, exist_ok=True)

    def _log(self, msg: str):
        logging.info(msg)
        try: self.log_queue.put_nowait(msg)
        except Exception: pass

    def set_mode(self, mode: str):
        if mode in self.engine.modes:
            self.mode = mode
            self._log(f"Mode set to {mode}")

    def set_gen_params(self, max_new_tokens: int, temperature: float):
        self.engine.default_max_new_tokens = max_new_tokens
        self.engine.default_temperature = temperature
        self._log(f"Gen params: max_new_tokens={max_new_tokens}, temperature={temperature}")

    def run_once(self, prompt_override: Optional[str]=None) -> Dict[str, Any]:
        telemetry = collect_telemetry()
        analysis = analyze_bottlenecks(telemetry)
        prompt = prompt_override or build_prompt(telemetry, analysis)

        aggregated, outputs = self.engine.aggregate(
            mode=self.mode, prompt=prompt,
            max_new_tokens=self.engine.default_max_new_tokens,
            temperature=self.engine.default_temperature,
            stop_event=self.stop_event
        )

        plan = extract_json(aggregated if isinstance(aggregated, str) else json.dumps(aggregated))
        confidence = None
        if plan and "confidence" in plan:
            try: confidence = float(plan["confidence"])
            except Exception: confidence = None

        if not validate_plan(plan) or (confidence is not None and confidence < 0.55):
            self._log("Plan invalid/low confidence; switching to blend.")
            self.set_mode("blend")
            aggregated, outputs = self.engine.aggregate(
                mode=self.mode, prompt=prompt,
                max_new_tokens=self.engine.default_max_new_tokens,
                temperature=self.engine.default_temperature,
                stop_event=self.stop_event
            )
            plan = extract_json(aggregated if isinstance(aggregated, str) else json.dumps(aggregated))

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(self.work_dir, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)

        json.dump(telemetry, open(os.path.join(run_dir,"telemetry.json"),"w"), indent=2)
        json.dump(analysis, open(os.path.join(run_dir,"analysis.json"),"w"), indent=2)
        json.dump(outputs, open(os.path.join(run_dir,"outputs.json"),"w"), indent=2)
        open(os.path.join(run_dir,"aggregated.txt"),"w").write(
            aggregated if isinstance(aggregated,str) else json.dumps(aggregated, indent=2)
        )

        exec_results = []
        if plan and validate_plan(plan):
            for task in plan["tasks"]:
                exec_results.append(execute_task(task, dry_run_default=True))
        else:
            self._log("No valid Python-only plan; artifacts saved.")

        json.dump(exec_results, open(os.path.join(run_dir,"exec_results.json"),"w"), indent=2)

        summary = {
            "run_dir": run_dir,
            "confidence": confidence,
            "valid_plan": bool(plan and validate_plan(plan)),
            "bottleneck_score": analysis["bottleneck_score"],
            "tasks_executed": exec_results,
        }
        self.last_summary = summary
        self.last_plan = plan
        self.last_outputs = outputs
        self.last_aggregated = aggregated if isinstance(aggregated, str) else json.dumps(aggregated, indent=2)
        self._log(f"Run complete: valid_plan={summary['valid_plan']}, confidence={confidence}, score={analysis['bottleneck_score']}")
        return summary

    def serve(self):
        self._log(f"Service started: interval={self.interval}s, mode={self.mode}")
        while not self.stop_event.is_set():
            try: self.run_once()
            except Exception as e: self._log(f"Service error: {e}")
            for _ in range(self.interval):
                if self.stop_event.is_set(): break
                time.sleep(1)
        self._log("Service stopped.")

    def start_service(self):
        self.stop_event.clear()
        t = threading.Thread(target=lambda: self.serve(), daemon=True)
        t.start()

    def stop_service(self):
        self.stop_event.set()

# ---------------------------
# Adapter discovery
# ---------------------------
def build_adapters() -> Dict[str, BaseLLMAdapter]:
    adapters = {}
    # Add your local HF models here (must be present locally/cached)
    hf_models = [
        "gpt2",
        "distilgpt2",
        # e.g., "meta-llama/Llama-2-7b-hf" (requires local weights & license)
        # e.g., "mistralai/Mistral-7B-Instruct-v0.2" (with local weights)
    ]
    for name in hf_models:
        try:
            adapters[name] = TransformersAdapter(name)
        except Exception as e:
            logging.warning(f"Skip HF model {name}: {e}")

    if not adapters:
        logging.error("No adapters loaded. Configure build_adapters() with your local models.")
    return adapters

# ---------------------------
# Compact GUI (Notebook)
# ---------------------------
class CompactDashboard:
    def __init__(self, root: tk.Tk, backend: OptimizerBackend):
        self.root = root
        self.backend = backend
        self.root.title("Python-only Optimizer Dashboard")
        try: self.root.tk.call('tk', 'scaling', 1.2)
        except Exception: pass

        # Top controls
        top = ttk.Frame(root); top.pack(fill="x", padx=6, pady=6)
        ttk.Label(top, text="Mode").pack(side="left")
        self.mode_var = tk.StringVar(value=backend.mode)
        ttk.Combobox(top, textvariable=self.mode_var, values=self.backend.engine.modes, width=8).pack(side="left", padx=6)
        ttk.Label(top, text="Max tokens").pack(side="left", padx=(12,4))
        self.max_tokens_var = tk.IntVar(value=self.backend.engine.default_max_new_tokens)
        ttk.Entry(top, textvariable=self.max_tokens_var, width=7).pack(side="left")
        ttk.Label(top, text="Temp").pack(side="left", padx=(12,4))
        self.temp_var = tk.DoubleVar(value=self.backend.engine.default_temperature)
        ttk.Entry(top, textvariable=self.temp_var, width=5).pack(side="left")
        ttk.Button(top, text="Apply", command=self.apply_settings).pack(side="left", padx=6)
        ttk.Button(top, text="Run once", command=self.run_once).pack(side="left", padx=6)
        ttk.Button(top, text="Start", command=self.start_service).pack(side="left", padx=6)
        ttk.Button(top, text="Stop", command=self.stop_service).pack(side="left", padx=6)

        # Notebook tabs
        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True, padx=6, pady=6)

        # Prompt tab
        prompt_frame = ttk.Frame(nb)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6)
        self.prompt_text.pack(fill="both", expand=True)
        nb.add(prompt_frame, text="Prompt")

        # Output tab
        output_frame = ttk.Frame(nb)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=14)
        self.output_text.pack(fill="both", expand=True)
        nb.add(output_frame, text="Output")

        # Telemetry tab
        telemetry_frame = ttk.Frame(nb)
        self.telemetry_text = scrolledtext.ScrolledText(telemetry_frame, height=12)
        self.telemetry_text.pack(fill="both", expand=True)
        nb.add(telemetry_frame, text="Telemetry")

        # Logs tab
        logs_frame = ttk.Frame(nb)
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=10)
        self.log_text.pack(fill="both", expand=True)
        nb.add(logs_frame, text="Logs")

        # Bottom status
        bottom = ttk.Frame(root); bottom.pack(fill="x", padx=6, pady=6)
        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100)
        self.progress.pack(fill="x", expand=True, side="left")
        self.status = ttk.Label(bottom, text="Ready"); self.status.pack(side="left", padx=10)
        self.conf_label = ttk.Label(bottom, text="Conf: - | Plan: - | Score: -")
        self.conf_label.pack(side="left", padx=10)

        # UI update timer
        self._schedule_updates()

    def apply_settings(self):
        self.backend.set_mode(self.mode_var.get())
        self.backend.set_gen_params(self.max_tokens_var.get(), self.temp_var.get())
        self._status("Settings applied.")

    def run_once(self):
        prompt_override = self.prompt_text.get("1.0", "end").strip() or None
        self._status("Running once...")
        threading.Thread(target=self._run_once_worker, args=(prompt_override,), daemon=True).start()

    def _run_once_worker(self, prompt_override):
        try:
            self.backend.run_once(prompt_override=prompt_override)
            self._status("Run completed.")
        except Exception as e:
            self._status(f"Run error: {e}")

    def start_service(self):
        self._status("Starting service...")
        self.backend.start_service()

    def stop_service(self):
        self.backend.stop_service()
        self._status("Stop requested.")

    def _status(self, msg):
        self.status.config(text=msg)

    def _schedule_updates(self):
        self._update_telemetry()
        self._drain_logs()
        self._update_outputs()
        val = (self.progress["value"] + 7) % 100
        self.progress["value"] = val
        self.root.after(800, self._schedule_updates)

    def _update_telemetry(self):
        telemetry = collect_telemetry()
        self.telemetry_text.delete("1.0", "end")
        self.telemetry_text.insert("end", json.dumps(telemetry, indent=2))

    def _drain_logs(self):
        drained = False
        while True:
            try:
                msg = self.backend.log_queue.get_nowait()
                self.log_text.insert("end", msg + "\n")
                self.log_text.see("end")
                drained = True
            except queue.Empty:
                break
        if drained:
            self.status.config(text="Updated logs")

    def _update_outputs(self):
        summary = self.backend.last_summary or {}
        aggregated = self.backend.last_aggregated or ""
        outputs = self.backend.last_outputs or {}

        conf = summary.get("confidence")
        valid = summary.get("valid_plan")
        score = summary.get("bottleneck_score")
        self.conf_label.config(text=f"Conf: {conf if conf is not None else '-'} | Plan: {valid if valid is not None else '-'} | Score: {score if score is not None else '-'}")

        self.output_text.delete("1.0", "end")
        if outputs:
            self.output_text.insert("end", "== Individual outputs ==\n")
            for name, text in outputs.items():
                self.output_text.insert("end", f"\n[{name}]\n{text}\n{'-'*60}\n")
        if aggregated:
            self.output_text.insert("end", f"\n== Aggregated ({self.backend.mode}) ==\n{aggregated}\n")

# ---------------------------
# Entry point
# ---------------------------
def build_backend(interval_seconds=75) -> OptimizerBackend:
    adapters = build_adapters()
    engine = EnsembleEngine(adapters)
    backend = OptimizerBackend(engine, interval=interval_seconds)
    return backend

def main(headless=False, interval_seconds=75):
    backend = build_backend(interval_seconds)
    if headless:
        backend.start_service()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            backend.stop_service()
    else:
        root = tk.Tk()
        try:
            style = ttk.Style(root)
            style.theme_use("clam")
        except Exception:
            pass
        app = CompactDashboard(root, backend)
        root.mainloop()

if __name__ == "__main__":
    main(headless=False, interval_seconds=90)

