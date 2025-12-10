import importlib
import subprocess
import sys
import os
import logging
import threading
import queue
import time
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

# ---------------------------
# Auto loader (on-demand pip)
# ---------------------------
def auto_import(package, import_name=None, extras=None):
    try:
        return importlib.import_module(import_name or package)
    except ImportError:
        logging.warning(f"Installing missing package: {package}{'['+extras+']' if extras else ''}")
        cmd = [sys.executable, "-m", "pip", "install", f"{package}[{extras}]" if extras else package]
        subprocess.check_call(cmd)
        return importlib.import_module(import_name or package)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Optional backends (install only if used)
transformers = None
llama_cpp = None
torch = None

# ---------------------------
# Model Adapters
# ---------------------------

class BaseLLMAdapter:
    def __init__(self, name):
        self.name = name

    def generate(self, prompt, max_new_tokens=512, temperature=0.7):
        raise NotImplementedError

    def score(self, text):
        """
        Heuristic confidence score: higher is better.
        You can improve by adding structure checks, keyword coverage, etc.
        """
        if not text:
            return 0.0
        # Simple structural heuristic: longer answers with code blocks and numbered steps score higher
        length = len(text)
        code_blocks = len(re.findall(r"```", text))
        steps = len(re.findall(r"^\s*\d+\.", text, flags=re.M))
        return 0.4 * min(length / 2000, 1.0) + 0.3 * min(code_blocks, 3) + 0.3 * min(steps, 10)

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

    def generate(self, prompt, max_new_tokens=512, temperature=0.7):
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
        logging.info(f"Loading llama.cpp model: {model_path}")
        self.llm = llama_cpp.Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads or os.cpu_count(),
        )

    def generate(self, prompt, max_new_tokens=512, temperature=0.7):
        out = self.llm(
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
        )
        return out["choices"][0]["text"]

# ---------------------------
# Ensemble Engine
# ---------------------------

class EnsembleEngine:
    def __init__(self, adapters):
        self.adapters = adapters  # dict name -> adapter
        self.modes = ["router", "vote", "cascade", "blend"]
        self.last_outputs = {}  # name -> text

    def query_all(self, prompt, max_new_tokens=512, temperature=0.7, progress_cb=None, stop_flag=None):
        results = {}

        def run_one(name, adapter):
            if stop_flag and stop_flag.is_set():
                return
            try:
                text = adapter.generate(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
                results[name] = text
                self.last_outputs[name] = text
                if progress_cb:
                    progress_cb(f"[{name}] done, len={len(text)}")
            except Exception as e:
                results[name] = f"ERROR: {e}"
                if progress_cb:
                    progress_cb(f"[{name}] error: {e}")

        threads = []
        for name, adapter in self.adapters.items():
            t = threading.Thread(target=run_one, args=(name, adapter), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return results

    def route_best(self, outputs):
        best_name = None
        best_score = -1
        for name, text in outputs.items():
            if text.startswith("ERROR"):
                continue
            score = self.adapters[name].score(text)
            if score > best_score:
                best_score = score
                best_name = name
        return best_name, outputs.get(best_name, "")

    def majority_vote(self, outputs):
        # Normalize by stripping whitespace and collapsing repeated spaces
        normalized = {k: re.sub(r"\s+", " ", v.strip()) for k, v in outputs.items() if not v.startswith("ERROR")}
        if not normalized:
            return "No valid outputs for voting."
        # Find most common normalized answer
        counts = {}
        for name, text in normalized.items():
            counts[text] = counts.get(text, 0) + 1
        consensus_text = max(counts.items(), key=lambda x: x[1])[0]
        # If consensus is weak, include a short diff summary
        if list(counts.values()).count(counts[consensus_text]) == 1 and len(counts) > 1:
            return self.blend(outputs)
        return consensus_text

    def cascade(self, outputs, preference_order=None):
        order = preference_order or list(self.adapters.keys())
        for name in order:
            text = outputs.get(name, "")
            if text and not text.startswith("ERROR"):
                return text
        return "No successful outputs in cascade."

    def blend(self, outputs):
        # Extract actionable steps/code blocks from all outputs and merge
        steps = []
        codes = []
        summaries = []

        for name, text in outputs.items():
            if text.startswith("ERROR"):
                continue
            # Extract numbered steps
            steps += re.findall(r"^\s*\d+\.\s.*", text, flags=re.M)
            # Extract code blocks
            block_matches = re.findall(r"```(.*?)```", text, flags=re.S)
            codes += block_matches
            # Short summary heuristics (first paragraph)
            first_para = text.strip().split("\n\n")[0]
            summaries.append(f"[{name}] {first_para[:500]}")

        merged = []
        if summaries:
            merged.append("Unified summary:\n" + "\n".join(summaries[:5]))
        if steps:
            merged.append("\nUnified steps:\n" + "\n".join(self._dedupe_lines(steps)))
        if codes:
            merged.append("\nUnified code blocks:\n" + "\n\n".join(self._dedupe_blocks(codes)))
        return "\n".join(merged) if merged else "No actionable content to blend."

    @staticmethod
    def _dedupe_lines(lines):
        seen = set()
        out = []
        for line in lines:
            key = re.sub(r"\s+", " ", line.strip()).lower()
            if key not in seen:
                seen.add(key)
                out.append(line)
        return out

    @staticmethod
    def _dedupe_blocks(blocks):
        seen = set()
        out = []
        for block in blocks:
            key = re.sub(r"\s+", " ", block.strip()).lower()
            if key not in seen:
                seen.add(key)
                out.append(f"```{block}```")
        return out

    def aggregate(self, mode, prompt, max_new_tokens=512, temperature=0.7, progress_cb=None, stop_flag=None):
        outputs = self.query_all(prompt, max_new_tokens, temperature, progress_cb, stop_flag)
        if mode == "router":
            _, best = self.route_best(outputs)
            return best, outputs
        elif mode == "vote":
            return self.majority_vote(outputs), outputs
        elif mode == "cascade":
            return self.cascade(outputs), outputs
        elif mode == "blend":
            return self.blend(outputs), outputs
        else:
            return "Unknown mode.", outputs

# ---------------------------
# GUI Application
# ---------------------------

class EnsembleGUI:
    def __init__(self, root, engine: EnsembleEngine):
        self.root = root
        self.engine = engine

        self.root.title("LLM Ensemble Bridge")
        self.stop_flag = threading.Event()

        # Top controls frame
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)

        ttk.Label(top, text="Ensemble mode:").pack(side="left")
        self.mode_var = tk.StringVar(value=engine.modes[0])
        self.mode_menu = ttk.Combobox(top, textvariable=self.mode_var, values=engine.modes, width=12)
        self.mode_menu.pack(side="left", padx=6)

        ttk.Label(top, text="Max tokens:").pack(side="left", padx=(12, 2))
        self.max_tokens_var = tk.IntVar(value=512)
        self.max_tokens_entry = ttk.Entry(top, textvariable=self.max_tokens_var, width=6)
        self.max_tokens_entry.pack(side="left")

        ttk.Label(top, text="Temperature:").pack(side="left", padx=(12, 2))
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_entry = ttk.Entry(top, textvariable=self.temp_var, width=6)
        self.temp_entry.pack(side="left")

        self.run_btn = ttk.Button(top, text="Run", command=self.run_ensemble)
        self.run_btn.pack(side="left", padx=8)
        self.stop_btn = ttk.Button(top, text="Stop", command=self.stop_run)
        self.stop_btn.pack(side="left", padx=4)

        # Model list box
        models_frame = ttk.LabelFrame(root, text="Loaded models")
        models_frame.pack(fill="x", padx=8, pady=8)
        self.models_list = scrolledtext.ScrolledText(models_frame, height=6, width=100)
        self.models_list.pack(fill="both", expand=True)
        self.models_list.insert("end", "\n".join([f"- {name}" for name in engine.adapters.keys()]))

        # Prompt input
        prompt_frame = ttk.LabelFrame(root, text="Prompt")
        prompt_frame.pack(fill="x", padx=8, pady=8)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=6, width=100)
        self.prompt_text.pack(fill="both", expand=True)

        # Progress and logs
        prog_frame = ttk.Frame(root)
        prog_frame.pack(fill="x", padx=8, pady=4)
        self.progress = ttk.Progressbar(prog_frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", expand=True)
        self.log_text = scrolledtext.ScrolledText(root, height=10, width=100)
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)

        # Output (aggregated)
        out_frame = ttk.LabelFrame(root, text="Aggregated output")
        out_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.output_text = scrolledtext.ScrolledText(out_frame, height=16, width=100)
        self.output_text.pack(fill="both", expand=True)

        # Execution controls
        exec_frame = ttk.LabelFrame(root, text="Execution preview & actions")
        exec_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.preview_text = scrolledtext.ScrolledText(exec_frame, height=8, width=100)
        self.preview_text.pack(fill="both", expand=True, pady=(4, 8))
        btns = ttk.Frame(exec_frame)
        btns.pack(fill="x")
        self.extract_code_btn = ttk.Button(btns, text="Extract code blocks", command=self.extract_code_blocks)
        self.extract_code_btn.pack(side="left", padx=4)
        self.save_btn = ttk.Button(btns, text="Save output", command=self.save_output)
        self.save_btn.pack(side="left", padx=4)
        self.exec_btn = ttk.Button(btns, text="Execute preview (sandboxed)", command=self.execute_preview)
        self.exec_btn.pack(side="left", padx=4)

        self._log("Ready. Load prompt and choose mode.")

    def _log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def _progress(self, msg=None):
        if msg:
            self._log(msg)
        # simple heartbeat progress
        val = (self.progress["value"] + 7) % 100
        self.progress["value"] = val

    def stop_run(self):
        self.stop_flag.set()
        self._log("Stop signal sent.")

    def run_ensemble(self):
        self.stop_flag.clear()
        mode = self.mode_var.get()
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            self._log("Provide a prompt.")
            return

        max_tokens = self.max_tokens_var.get()
        temp = self.temp_var.get()

        def progress_cb(msg):
            self._progress(msg)

        def worker():
            try:
                agg, outputs = self.engine.aggregate(
                    mode=mode,
                    prompt=prompt,
                    max_new_tokens=max_tokens,
                    temperature=temp,
                    progress_cb=progress_cb,
                    stop_flag=self.stop_flag
                )
                # Show individual outputs
                self.output_text.delete("1.0", "end")
                self.output_text.insert("end", f"== Individual outputs ==\n")
                for name, text in outputs.items():
                    self.output_text.insert("end", f"\n[{name}]\n{text}\n{'-'*60}\n")
                # Show aggregated
                self.output_text.insert("end", f"\n== Aggregated ({mode}) ==\n{agg}\n")
                self.output_text.see("end")
                self._log("Aggregation complete.")
            except Exception as e:
                self._log(f"Aggregation error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def extract_code_blocks(self):
        content = self.output_text.get("1.0", "end")
        blocks = re.findall(r"```(.*?)```", content, flags=re.S)
        if not blocks:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("end", "# No code blocks found.\n")
            return
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", "\n\n".join([b.strip() for b in blocks]))
        self._log(f"Extracted {len(blocks)} code block(s).")

    def save_output(self):
        content = self.output_text.get("1.0", "end")
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(f"Saved output to {path}")

    def execute_preview(self):
        code = self.preview_text.get("1.0", "end").strip()
        if not code:
            self._log("No code in preview.")
            return
        self._log("Executing preview in sandbox...")
        sandbox_globals = {"__builtins__": {"print": print, "range": range, "len": len}}
        try:
            exec(code, sandbox_globals, {})
            self._log("Preview executed.")
        except Exception as e:
            self._log(f"Execution error: {e}")

# ---------------------------
# Assembly & startup
# ---------------------------

def build_adapters():
    """
    Detect and assemble available local models.
    - Add any HuggingFace model IDs you have locally.
    - Add llama.cpp model paths if you use GGUF files.
    """
    adapters = {}
    # Example: Transformers models installed or cached locally
    hf_models = [
        "gpt2",
        "distilgpt2",
        # Add your local HF models here, e.g.:
        # "TheBloke/Mistral-7B-Instruct-v0.2-GGUF" (if using Transformers with text-generation-inference)
        # "meta-llama/Llama-2-7b-hf" (needs weights locally and license)
    ]
    for name in hf_models:
        try:
            adapters[name] = TransformersAdapter(name)
        except Exception as e:
            logging.warning(f"Skip Transformers model {name}: {e}")

    # Example: llama.cpp local files (GGUF)
    gguf_candidates = [
        # r"C:\models\llama-2-7b.Q4_K_M.gguf",
        # "/models/mistral-7b-instruct.Q4_K_M.gguf",
    ]
    for path in gguf_candidates:
        if os.path.exists(path):
            try:
                base = os.path.basename(path)
                adapters[f"llama.cpp:{base}"] = LlamaCppAdapter(model_path=path, name=base)
            except Exception as e:
                logging.warning(f"Skip llama.cpp model {path}: {e}")

    if not adapters:
        logging.error("No adapters loaded. Please configure local models in build_adapters().")
    return adapters

def main():
    adapters = build_adapters()
    engine = EnsembleEngine(adapters=adapters)

    root = tk.Tk()
    # High-DPI friendly defaults
    try:
        root.tk.call('tk', 'scaling', 1.2)
    except Exception:
        pass
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = EnsembleGUI(root, engine)
    root.mainloop()

if __name__ == "__main__":
    main()

