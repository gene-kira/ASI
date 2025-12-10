import importlib
import subprocess
import sys
import os
import json
import time
import re
import logging
import threading
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
llama_cpp = None

# ---------------------------
# Model adapters
# ---------------------------
class BaseLLMAdapter:
    def __init__(self, name):
        self.name = name

    def generate(self, prompt, max_new_tokens=1024, temperature=0.4):
        raise NotImplementedError

    def score(self, text: str) -> float:
        if not text or text.startswith("ERROR"):
            return 0.0
        length = len(text)
        has_json = bool(re.search(r"\{.*\}", text, flags=re.S))
        steps = len(re.findall(r"^\s*\d+\.", text, flags=re.M))
        code_blocks = len(re.findall(r"```", text))
        return (
            0.35 * min(length / 4000, 1.0)
            + 0.25 * (1.0 if has_json else 0.0)
            + 0.2 * min(steps, 10) / 10
            + 0.2 * min(code_blocks, 3) / 3
        )

class TransformersAdapter(BaseLLMAdapter):
    def __init__(self, name, device="cpu"):
        global transformers, torch
        if transformers is None:
            transformers = auto_import("transformers")
        if torch is None:
            torch = auto_import("torch")
        super().__init__(name)
        logging.info(f"Loading Transformers model: {name}")
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(name)
        self.model = transformers.AutoModelForCausalLM.from_pretrained(name)
        self.device = device
        try:
            self.model.to(device)
        except Exception as e:
            logging.warning(f"Device move failed, using CPU: {e}")

    def generate(self, prompt, max_new_tokens=1024, temperature=0.4):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

class LlamaCppAdapter(BaseLLMAdapter):
    def __init__(self, model_path, name=None, n_ctx=4096, n_threads=None):
        global llama_cpp
        if llama_cpp is None:
            llama_cpp = auto_import("llama_cpp", "llama_cpp")
        super().__init__(name or os.path.basename(model_path))
        logging.info(f"Loading llama.cpp: {model_path}")
        self.llm = llama_cpp.Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads or os.cpu_count(),
        )

    def generate(self, prompt, max_new_tokens=1024, temperature=0.4):
        out = self.llm(
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
        )
        return out["choices"][0]["text"]

# ---------------------------
# Ensemble engine
# ---------------------------
class EnsembleEngine:
    def __init__(self, adapters: Dict[str, BaseLLMAdapter]):
        self.adapters = adapters
        self.modes = ["router", "vote", "cascade", "blend"]
        self.last_outputs: Dict[str, str] = {}
        # Defaults; GUI can override
        self.default_max_new_tokens = 1200
        self.default_temperature = 0.35

    def query_all(self, prompt, max_new_tokens=None, temperature=None, stop_event: Optional[threading.Event]=None):
        results = {}
        threads = []
        max_new_tokens = max_new_tokens or self.default_max_new_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        def run_one(name, adapter):
            if stop_event and stop_event.is_set():
                return
            try:
                text = adapter.generate(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
                results[name] = text
                self.last_outputs[name] = text
            except Exception as e:
                results[name] = f"ERROR: {e}"

        for name, adapter in self.adapters.items():
            t = threading.Thread(target=run_one, args=(name, adapter), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        return results

    def route_best(self, outputs):
        best_name, best_score = None, -1
        for name, text in outputs.items():
            sc = self.adapters[name].score(text)
            if sc > best_score:
                best_name, best_score = name, sc
        return best_name, outputs.get(best_name, "")

    def majority_vote(self, outputs):
        normalized = {k: re.sub(r"\s+", " ", v.strip()) for k, v in outputs.items() if not v.startswith("ERROR")}
        if not normalized:
            return "No valid outputs for voting."
        counts = {}
        for _, txt in normalized.items():
            counts[txt] = counts.get(txt, 0) + 1
        return max(counts.items(), key=lambda x: x[1])[0]

    def cascade(self, outputs, order=None):
        order = order or list(self.adapters.keys())
        for name in order:
            txt = outputs.get(name, "")
            if txt and not txt.startswith("ERROR"):
                return txt
        return "No successful outputs in cascade."

    def blend(self, outputs):
        steps, codes, summaries = [], [], []
        for name, text in outputs.items():
            if text.startswith("ERROR"):
                continue
            steps += re.findall(r"^\s*\d+\.\s.*", text, flags=re.M)
            codes += re.findall(r"```(.*?)```", text, flags=re.S)
            first = text.strip().split("\n\n")[0]
            summaries.append(f"[{name}] {first[:600]}")
        merged = []
        if summaries:
            merged.append("Unified summary:\n" + "\n".join(summaries[:6]))
        if steps:
            merged.append("\nUnified steps:\n" + "\n".join(self._dedupe_lines(steps)))
        if codes:
            merged.append("\nUnified code blocks:\n" + "\n\n".join(self._dedupe_blocks(codes)))
        return "\n".join(merged) if merged else "No actionable content to blend."

    @staticmethod
    def _dedupe_lines(lines):
        seen, out = set(), []
        for line in lines:
            key = re.sub(r"\s+", " ", line.strip()).lower()
            if key not in seen:
                seen.add(key)
                out.append(line)
        return out

    @staticmethod
    def _dedupe_blocks(blocks):
        seen, out = set(), []
        for block in blocks:
            key = re.sub(r"\s+", " ", block.strip()).lower()
            if key not in seen:
                seen.add(key)
                out.append(f"```{block}```")
        return out

    def aggregate(self, mode, prompt, max_new_tokens=None, temperature=None, stop_event=None):
        outputs = self.query_all(prompt, max_new_tokens, temperature, stop_event)
        if mode == "router":
            _, best = self.route_best(outputs)
            return best, outputs
        if mode == "vote":
            return self.majority_vote(outputs), outputs
        if mode == "cascade":
            return self.cascade(outputs), outputs
        if mode == "blend":
            return self.blend(outputs), outputs
        return "Unknown mode.", outputs

# ---------------------------
# Telemetry collection
# ---------------------------
def collect_telemetry() -> Dict[str, Any]:
    net = psutil.net_io_counters()
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            procs.append({
                "pid": info.get("pid"),
                "name": info.get("name"),
                "cpu": info.get("cpu_percent"),
                "rss_mb": round((info.get("memory_info").rss if info.get("memory_info") else 0) / (1024 * 1024), 2)
            })
        except Exception:
            pass
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": round(mem.used / (1024 * 1024), 2),
        "disk_percent": disk.percent,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
        "top_processes": sorted(procs, key=lambda x: (x["cpu"] or 0), reverse=True)[:8]
    }

# ---------------------------
# JSON plan schema & validation
# ---------------------------
PLAN_SCHEMA = {
    "required": ["confidence", "summary", "tasks"],
    "tasks_required": ["id", "intent", "lang", "code", "dry_run", "risk"],
}

def plan_prompt(telemetry: Dict[str, Any]) -> str:
    return f"""
You are an autonomous orchestration ensemble. Given system telemetry (JSON below), produce a structured maintenance plan as JSON that adheres to this schema:

schema:
{json.dumps(PLAN_SCHEMA, indent=2)}

rules:
- Return ONLY valid JSON with keys: confidence(float 0..1), summary(string), tasks(list).
- Each task must include: id(string), intent(string), lang(one of: bash|powershell|python), code(string), dry_run(bool), risk(string: low|medium|high), notes(optional).
- Prefer safe actions and mark risky tasks as dry_run=true.
- Keep code self-contained and idempotent.

telemetry:
{json.dumps(telemetry, indent=2)}
"""

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return None
    raw = match.group(0)
    try:
        return json.loads(raw)
    except Exception:
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        cleaned = re.sub(r"(\w+):", r'"\1":', cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            return None

def validate_plan(plan: Dict[str, Any]) -> bool:
    if not plan:
        return False
    for k in PLAN_SCHEMA["required"]:
        if k not in plan:
            return False
    if not isinstance(plan.get("tasks"), list):
        return False
    for t in plan["tasks"]:
        for tk in PLAN_SCHEMA["tasks_required"]:
            if tk not in t:
                return False
        if t["lang"] not in ["bash", "powershell", "python"]:
            return False
        if t["risk"] not in ["low", "medium", "high"]:
            return False
    return True

# ---------------------------
# Safe executor
# ---------------------------
ALLOWED_ENVS = {
    "print": print,
    "range": range,
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
}

def execute_task(task: Dict[str, Any], dry_run_default=True) -> Dict[str, Any]:
    lang = task["lang"]
    code = task["code"]
    dry_run = task.get("dry_run", dry_run_default)

    result = {"id": task["id"], "status": "skipped", "error": None}

    try:
        if dry_run:
            result["status"] = "dry_run"
            return result

        if lang == "python":
            sandbox_globals = {"__builtins__": ALLOWED_ENVS}
            exec(code, sandbox_globals, {})
            result["status"] = "executed"
        elif lang == "bash":
            import subprocess
            cp = subprocess.run(code, shell=True, capture_output=True, text=True)
            result["status"] = "executed" if cp.returncode == 0 else "error"
            result["stdout"] = cp.stdout
            result["stderr"] = cp.stderr
            result["returncode"] = cp.returncode
        elif lang == "powershell":
            import subprocess
            cmd = ["powershell", "-NoProfile", "-Command", code]
            cp = subprocess.run(cmd, capture_output=True, text=True)
            result["status"] = "executed" if cp.returncode == 0 else "error"
            result["stdout"] = cp.stdout
            result["stderr"] = cp.stderr
            result["returncode"] = cp.returncode
        else:
            result["status"] = "error"
            result["error"] = f"Unsupported lang: {lang}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result

# ---------------------------
# Autonomous backend
# ---------------------------
class AutonomousBackend:
    def __init__(self, adapters: Dict[str, BaseLLMAdapter], work_dir="ensemble_runs"):
        self.engine = EnsembleEngine(adapters)
        self.work_dir = work_dir
        self.mode = "router"
        self.interval_seconds = 60
        self.stop_event = threading.Event()
        self.last_summary: Dict[str, Any] = {}
        self.last_outputs: Dict[str, str] = {}
        self.last_aggregated: str = ""
        self.log_queue: "queue.Queue[str]" = queue.Queue()
        os.makedirs(self.work_dir, exist_ok=True)

    def set_mode(self, mode: str):
        if mode in self.engine.modes:
            self.mode = mode
            self._log(f"Mode changed to {mode}")
        else:
            self._log(f"Ignoring unknown mode: {mode}")

    def set_gen_params(self, max_new_tokens: int, temperature: float):
        self.engine.default_max_new_tokens = max_new_tokens
        self.engine.default_temperature = temperature
        self._log(f"Gen params set: max_new_tokens={max_new_tokens}, temperature={temperature}")

    def _log(self, msg: str):
        logging.info(msg)
        try:
            self.log_queue.put_nowait(msg)
        except Exception:
            pass

    def run_once(self, prompt_override: Optional[str] = None) -> Dict[str, Any]:
        telemetry = collect_telemetry()
        prompt = prompt_override or plan_prompt(telemetry)

        aggregated, outputs = self.engine.aggregate(
            mode=self.mode,
            prompt=prompt,
            max_new_tokens=self.engine.default_max_new_tokens,
            temperature=self.engine.default_temperature,
            stop_event=self.stop_event
        )

        plan = extract_json(aggregated if isinstance(aggregated, str) else json.dumps(aggregated))
        confidence = None
        if plan and "confidence" in plan:
            try:
                confidence = float(plan["confidence"])
            except Exception:
                confidence = None

        if not validate_plan(plan) or (confidence is not None and confidence < 0.55):
            self._log("Plan invalid/low confidence; switching to blend mode.")
            self.mode = "blend"
            aggregated, outputs = self.engine.aggregate(
                mode=self.mode,
                prompt=prompt,
                max_new_tokens=self.engine.default_max_new_tokens,
                temperature=self.engine.default_temperature,
                stop_event=self.stop_event
            )
            plan = extract_json(aggregated if isinstance(aggregated, str) else json.dumps(aggregated))

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(self.work_dir, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)

        with open(os.path.join(run_dir, "telemetry.json"), "w", encoding="utf-8") as f:
            json.dump(telemetry, f, indent=2)
        with open(os.path.join(run_dir, "outputs.json"), "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2)
        with open(os.path.join(run_dir, "aggregated.txt"), "w", encoding="utf-8") as f:
            f.write(aggregated if isinstance(aggregated, str) else json.dumps(aggregated, indent=2))

        exec_results = []
        if plan and validate_plan(plan):
            for task in plan["tasks"]:
                exec_results.append(execute_task(task, dry_run_default=True))
        else:
            self._log("No valid plan to execute; artifacts saved.")

        with open(os.path.join(run_dir, "exec_results.json"), "w", encoding="utf-8") as f:
            json.dump(exec_results, f, indent=2)

        summary = {
            "run_dir": run_dir,
            "confidence": confidence,
            "valid_plan": bool(plan and validate_plan(plan)),
            "tasks_executed": exec_results,
        }
        self.last_summary = summary
        self.last_outputs = outputs
        self.last_aggregated = aggregated if isinstance(aggregated, str) else json.dumps(aggregated, indent=2)
        self._log(f"Run complete: valid_plan={summary['valid_plan']}, confidence={confidence}")
        return summary

    def serve(self):
        self._log(f"Service started: interval={self.interval_seconds}s, mode={self.mode}")
        while not self.stop_event.is_set():
            try:
                self.run_once()
            except Exception as e:
                self._log(f"Service error: {e}")
            finally:
                for _ in range(self.interval_seconds):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        self._log("Service stopped.")

    def start_service(self):
        self.stop_event.clear()
        t = threading.Thread(target=selfserve_wrapper, args=(self,), daemon=True)
        t.start()

    def stop_service(self):
        self.stop_event.set()

def selfserve_wrapper(backend: AutonomousBackend):
    backend.serve()

# ---------------------------
# Adapter discovery
# ---------------------------
def build_adapters() -> Dict[str, BaseLLMAdapter]:
    adapters = {}
    # Add your local HuggingFace models here
    hf_models = [
        "gpt2",
        "distilgpt2",
        # e.g., "meta-llama/Llama-2-7b-hf" (requires local weights & license)
    ]
    for name in hf_models:
        try:
            adapters[name] = TransformersAdapter(name)
        except Exception as e:
            logging.warning(f"Skip HF model {name}: {e}")

    # Add local GGUF files for llama.cpp here
    gguf_paths = [
        # r"C:\models\mistral-7b-instruct.Q4_K_M.gguf",
        # "/models/llama-2-7b.Q4_K_M.gguf",
    ]
    for path in gguf_paths:
        if os.path.exists(path):
            try:
                base = os.path.basename(path)
                adapters[f"llama.cpp:{base}"] = LlamaCppAdapter(model_path=path, name=base)
            except Exception as e:
                logging.warning(f"Skip llama.cpp {path}: {e}")

    if not adapters:
        logging.error("No adapters loaded. Configure build_adapters() with your local models.")
    return adapters

# ---------------------------
# Compact GUI (Notebook)
# ---------------------------
class CompactDashboard:
    def __init__(self, root: tk.Tk, backend: AutonomousBackend):
        self.root = root
        self.backend = backend
        self.root.title("LLM Ensemble Dashboard")
        try:
            self.root.tk.call('tk', 'scaling', 1.2)
        except Exception:
            pass

        # Top controls row
        top = ttk.Frame(root); top.pack(fill="x", padx=6, pady=6)
        ttk.Label(top, text="Mode").pack(side="left")
        self.mode_var = tk.StringVar(value=backend.mode)
        self.mode_menu = ttk.Combobox(top, textvariable=self.mode_var, values=backend.engine.modes, width=10)
        self.mode_menu.pack(side="left", padx=6)

        ttk.Label(top, text="Max tokens").pack(side="left", padx=(12, 4))
        self.max_tokens_var = tk.IntVar(value=backend.engine.default_max_new_tokens)
        ttk.Entry(top, textvariable=self.max_tokens_var, width=7).pack(side="left")

        ttk.Label(top, text="Temp").pack(side="left", padx=(12, 4))
        self.temp_var = tk.DoubleVar(value=backend.engine.default_temperature)
        ttk.Entry(top, textvariable=self.temp_var, width=5).pack(side="left")

        ttk.Button(top, text="Apply", command=self.apply_settings).pack(side="left", padx=6)
        ttk.Button(top, text="Run once", command=self.run_once).pack(side="left", padx=6)
        ttk.Button(top, text="Start service", command=self.start_service).pack(side="left", padx=6)
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
        self.status = ttk.Label(bottom, text="Ready")
        self.status.pack(side="left", padx=10)
        self.conf_label = ttk.Label(bottom, text="Conf: - | Plan: -")
        self.conf_label.pack(side="left", padx=10)

        # UI update timer
        self._schedule_updates()

    def apply_settings(self):
        mode = self.mode_var.get()
        self.backend.set_mode(mode)
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
        # Telemetry
        self._update_telemetry()
        # Logs
        self._drain_logs()
        # Outputs and summary
        self._update_outputs()
        # Progress heartbeat
        val = (self.progress["value"] + 7) % 100
        self.progress["value"] = val
        # Re-run every 800ms
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
            # subtle UI cue
            self.status.config(text="Updated logs")

    def _update_outputs(self):
        summary = self.backend.last_summary or {}
        aggregated = self.backend.last_aggregated or ""
        outputs = self.backend.last_outputs or {}

        # Confidence/validity
        conf = summary.get("confidence")
        valid = summary.get("valid_plan")
        self.conf_label.config(text=f"Conf: {conf if conf is not None else '-'} | Plan: {valid if valid is not None else '-'}")

        # Output pane
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
def main(headless=False, interval_seconds=60):
    adapters = build_adapters()
    backend = AutonomousBackend(adapters=adapters)
    backend.interval_seconds = interval_seconds

    if headless:
        # Headless service
        svc_thread = threading.Thread(target=selfserve_wrapper, args=(backend,), daemon=True)
        svc_thread.start()
        try:
            while svc_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            backend.stop_service()
    else:
        # GUI mode
        root = tk.Tk()
        try:
            style = ttk.Style(root)
            style.theme_use("clam")
        except Exception:
            pass
        app = CompactDashboard(root, backend)
        root.mainloop()

if __name__ == "__main__":
    # Set headless=True to run as pure backend service
    main(headless=False, interval_seconds=90)

