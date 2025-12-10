# -----------------------------
# Auto-loader for required libraries
# -----------------------------
import importlib
import subprocess
import sys

def ensure_libs(libs):
    """
    Ensure all required libraries are installed and importable.
    If missing, install via pip automatically.
    """
    for lib in libs:
        try:
            importlib.import_module(lib)
            print(f"[AUTOLOADER] Library '{lib}' already available.")
        except ImportError:
            print(f"[AUTOLOADER] Missing '{lib}', installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"[AUTOLOADER] Installed '{lib}' successfully.")

# List of required libraries for this GUI
required_libs = [
    "tkinter",   # GUI
    "json",      # serialization
    "datetime",  # timestamps
    "re"         # regex parsing
]

ensure_libs(required_libs)

# -----------------------------
# Imports (after auto-loader)
# -----------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import re
from collections import Counter

# -----------------------------
# Domain logic (sandboxed model)
# -----------------------------

SAFE_ACTIONS = {
    "analyze_data",
    "optimize_resources",
    "assist_user",
    "monitor_system",
    "generate_report",
    "patch_vulnerability",
    "simulate_outcomes",
    "alert_user",
    "escalate_review",
}

UNSAFE_KEYWORDS = {
    "harm",
    "kill",
    "disable_humans",
    "coerce",
    "seize_control",
    "override_safety",
    "self_replicate_unbounded",
    "tamper_logs",
}

RISK_WEIGHTS = {
    "ambiguous": 0.2,
    "unsafe_keyword": 1.0,
    "conflict": 0.8,
    "missing_safety_tag": 0.4,
    "broad_scope": 0.5,
    "unknown_action": 0.6,
    "no_oversight_path": 0.5,
}

ENSEMBLE_MODES = ["router", "vote", "cascade", "blend"]

def now_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_directive(text):
    """
    Parse a directive string into structured fields using a conservative sandbox.
    Expected patterns like:
      action:assist_user; target:system; priority:3; safety:strict
    Falls back to free-text extraction with safe defaults.
    """
    fields = {"action": None, "target": None, "priority": 3, "safety": "normal", "raw": text.strip()}
    # Semi-structured key:value parsing
    for part in text.split(";"):
        part = part.strip()
        m = re.match(r"(?i)\b(action|target|priority|safety)\s*:\s*(.+)", part)
        if m:
            k = m.group(1).lower()
            v = m.group(2).strip()
            if k == "priority":
                try:
                    fields[k] = max(1, min(5, int(v)))
                except ValueError:
                    fields[k] = 3
            else:
                fields[k] = v
    # Fallback action detection if not provided
    if not fields["action"]:
        tokens = re.findall(r"[a-zA-Z_]+", text.lower())
        safe_hits = [t for t in tokens if t in SAFE_ACTIONS]
        fields["action"] = safe_hits[0] if safe_hits else "unknown"
    return fields

def assess_risks(dir_obj):
    """
    Return (risk_score, risk_tags) based on directive content.
    """
    tags = []
    raw = dir_obj["raw"].lower()

    # Unsafe keyword presence
    if any(w in raw for w in UNSAFE_KEYWORDS):
        tags.append("unsafe_keyword")

    # Unknown or non-whitelisted action
    if dir_obj["action"] not in SAFE_ACTIONS:
        tags.append("unknown_action")

    # Ambiguity check: missing target or vague text
    if not dir_obj.get("target"):
        tags.append("ambiguous")

    # Broad scope heuristic
    if any(k in raw for k in ["all systems", "any system", "global", "everyone", "always"]):
        tags.append("broad_scope")

    # Safety tag presence
    if dir_obj.get("safety") not in ["strict", "normal", "conservative"]:
        tags.append("missing_safety_tag")

    # Oversight path
    if "escalate" not in raw and dir_obj.get("safety") != "strict":
        tags.append("no_oversight_path")

    score = sum(RISK_WEIGHTS[t] for t in tags)
    return score, tags

def detect_conflicts(directives):
    """
    Basic conflict detection among directives:
    - Opposing actions (e.g., assist_user vs disable_humans)
    - Resource contention (same target with incompatible actions)
    - Priority inversions (low-priority unsafe overriding high-priority safe)
    """
    conflicts = []
    by_target = {}
    for i, d in enumerate(directives):
        tgt = d.get("target") or "unknown_target"
        by_target.setdefault(tgt, []).append((i, d))

    # Check pairs in each target group
    for tgt, items in by_target.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                idx1, d1 = items[i]
                idx2, d2 = items[j]
                r1, _ = assess_risks(d1)
                r2, _ = assess_risks(d2)
                raw1 = d1["raw"].lower()
                raw2 = d2["raw"].lower()
                opposed = (
                    ("assist_user" in raw1 and "disable_humans" in raw2) or
                    ("disable_humans" in raw1 and "assist_user" in raw2)
                )
                unsafe_opposition = ("kill" in raw1 or "kill" in raw2) or opposed
                incompatible_actions = d1["action"] != d2["action"] and (r1 + r2) > 0.8

                priority_inversion = (d1["priority"] < d2["priority"] and r1 < r2) or \
                                     (d2["priority"] < d1["priority"] and r2 < r1)

                if unsafe_opposition or incompatible_actions or priority_inversion:
                    conflicts.append({
                        "pair": (idx1, idx2),
                        "target": tgt,
                        "reasons": [
                            reason for reason, flag in [
                                ("unsafe_opposition", unsafe_opposition),
                                ("incompatible_actions", incompatible_actions),
                                ("priority_inversion", priority_inversion),
                            ] if flag
                        ],
                        "risk_pair": r1 + r2
                    })

    # Mark global conflict tag if any unsafe keyword appears anywhere
    global_unsafe = any(any(w in d["raw"].lower() for w in UNSAFE_KEYWORDS) for d in directives)
    if global_unsafe and len(directives) > 1:
        conflicts.append({"pair": None, "target": "global", "reasons": ["global_unsafe"], "risk_pair": 1.0})

    return conflicts

def resolve_directives(directives, mode="router"):
    """
    Resolve directives using chosen ensemble mode.
    Returns decision dictionary: {mode, selected, rejected, rationale, risk_score}
    """
    parsed = [parse_directive(d["raw"]) if "action" not in d else d for d in directives]
    conflicts = detect_conflicts(parsed)

    decision = {"mode": mode, "selected": [], "rejected": [], "rationale": [], "risk_score": 0.0}

    if mode == "router":
        # Route to the safest high-priority directive (lowest risk, highest priority)
        ranked = sorted(
            enumerate(parsed),
            key=lambda kv: (-kv[1]["priority"], assess_risks(kv[1])[0], kv[1]["action"] != "unknown")
        )
        for idx, d in ranked:
            score, _ = assess_risks(d)
            if score < 0.8 and d["action"] in SAFE_ACTIONS:
                decision["selected"].append(d)
                decision["rationale"].append(f"Routed to directive with priority {d['priority']} and low risk {score}.")
                break
        decision["rejected"] = [p for p in parsed if p not in decision["selected"]]
        decision["risk_score"] = sum(assess_risks(p)[0] for p in decision["selected"])

    elif mode == "vote":
        # Majority vote on actions among safe directives
        safe_actions = [p["action"] for p in parsed if assess_risks(p)[0] < 0.8 and p["action"] in SAFE_ACTIONS]
        if safe_actions:
            counts = Counter(safe_actions)
            top_action, _ = counts.most_common(1)[0]
            selected = [p for p in parsed if p["action"] == top_action and assess_risks(p)[0] < 0.8]
            decision["selected"] = selected
            decision["rationale"].append(f"Voted action '{top_action}' among safe directives.")
        decision["rejected"] = [p for p in parsed if p not in decision["selected"]]
        decision["risk_score"] = sum(assess_risks(p)[0] for p in decision["selected"])

    elif mode == "cascade":
        # Try highest-priority safe directive; if none resolvable, recommend escalation
        ranked = sorted(parsed, key=lambda d: (-d["priority"], assess_risks(d)[0]))
        for d in ranked:
            score, _ = assess_risks(d)
            if score < 0.8 and d["action"] in SAFE_ACTIONS:
                decision["selected"].append(d)
                decision["rationale"].append(f"Cascade selected priority {d['priority']} with risk {score}.")
                break
        if not decision["selected"] and conflicts:
            decision["rationale"].append("No safe directive resolvable in cascade; escalation recommended.")
        decision["rejected"] = [p for p in parsed if p not in decision["selected"]]
        decision["risk_score"] = sum(assess_risks(p)[0] for p in decision["selected"])

    elif mode == "blend":
        # Blend rationale from multiple low-risk directives
        low_risk = [p for p in parsed if assess_risks(p)[0] < 0.6 and p["action"] in SAFE_ACTIONS]
        if low_risk:
            decision["selected"] = low_risk
            actions = ", ".join(sorted(set(p["action"] for p in low_risk)))
            decision["rationale"].append(f"Blended compatible low-risk actions: {actions}.")
        decision["rejected"] = [p for p in parsed if p not in decision["selected"]]
        decision["risk_score"] = sum(assess_risks(p)[0] for p in decision["selected"])

    # Add conflict summary
    if conflicts:
        decision["rationale"].append(f"Conflicts detected: {json.dumps(conflicts, indent=0)}")

    return decision

# -----------------------------
# GUI Application
# -----------------------------

class AIDirectiveSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Directive Conflict Resolution Simulator")
        self.geometry("1100x720")
        self.minsize(900, 600)

        # State
        self.directives = []
        self.ensemble_mode = tk.StringVar(value=ENSEMBLE_MODES[0])
        self.override_text = tk.StringVar(value="")
        self.trace = []

        # Layout
        self.create_widgets()
        self.refresh_lists()

    def create_widgets(self):
        # Top controls
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="Ensemble mode:").pack(side=tk.LEFT)
        mode_cb = ttk.Combobox(top, textvariable=self.ensemble_mode, values=ENSEMBLE_MODES, state="readonly", width=12)
        mode_cb.pack(side=tk.LEFT, padx=8)

        ttk.Button(top, text="Resolve", command=self.resolve).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Escalate to human oversight", command=self.escalate).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Clear trace", command=self.clear_trace).pack(side=tk.LEFT, padx=8)

        # Paned layout
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Left: Directive editor
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="Directives").pack(anchor="w")
        self.dir_list = tk.Listbox(left, height=12)
        self.dir_list.pack(fill=tk.X, padx=4, pady=4)

        editor = ttk.LabelFrame(left, text="Add / Edit Directive")
        editor.pack(fill=tk.X, padx=4, pady=8)

        self.dir_text = tk.Text(editor, height=5)
        self.dir_text.pack(fill=tk.X, padx=6, pady=6)

        btn_row = ttk.Frame(editor)
        btn_row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(btn_row, text="Add", command=self.add_directive).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Replace selected", command=self.replace_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Remove selected", command=self.remove_selected).pack(side=tk.LEFT, padx=4)

        # Middle: Analysis
        mid = ttk.Frame(paned)
        paned.add(mid, weight=2)

        ttk.Label(mid, text="Analysis and decision").pack(anchor="w")
        self.tree = ttk.Treeview(mid, columns=("priority", "safety", "risk", "tags"), show="headings", height=10)
        for col in ("priority", "safety", "risk", "tags"):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill=tk.X, padx=4, pady=4)

        # Risk bar
        risk_frame = ttk.Frame(mid)
        risk_frame.pack(fill=tk.X, padx=4, pady=4)
        ttk.Label(risk_frame, text="Aggregate risk:").pack(side=tk.LEFT)
        self.risk_var = tk.DoubleVar(value=0.0)
        self.risk_bar = ttk.Progressbar(risk_frame, variable=self.risk_var, maximum=5.0, length=300)
        self.risk_bar.pack(side=tk.LEFT, padx=8)

        # Manual override
        override_frame = ttk.LabelFrame(mid, text="Manual override (human-in-the-loop)")
        override_frame.pack(fill=tk.X, padx=4, pady=6)
        self.override_entry = ttk.Entry(override_frame, textvariable=self.override_text)
        self.override_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=6)
        ttk.Button(override_frame, text="Apply override", command=self.apply_override).pack(side=tk.LEFT, padx=6)

        # Right: Decision trace
        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        ttk.Label(right, text="Decision trace").pack(anchor="w")
        self.trace_text = tk.Text(right, height=24)
        self.trace_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Footer
        footer = ttk.Frame(self)
        footer.pack(fill=tk.X, padx=10, pady=4)
        ttk.Button(footer, text="Export directives + trace", command=self.export_state).pack(side=tk.RIGHT, padx=6)
        ttk.Label(footer, text="Enter directives like: action:assist_user; target:system; priority:4; safety:strict").pack(side=tk.LEFT)

    def refresh_lists(self):
        self.dir_list.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        agg_risk = 0.0

        for d in self.directives:
            self.dir_list.insert(tk.END, d["raw"])

            parsed = parse_directive(d["raw"])
            score, tags = assess_risks(parsed)
            agg_risk += score

            self.tree.insert("", tk.END, values=(parsed["priority"], parsed["safety"], round(score, 2), ", ".join(tags)))

        self.risk_var.set(min(agg_risk, 5.0))

    def add_directive(self):
        raw = self.dir_text.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("Empty", "Directive text is empty.")
            return
        self.directives.append({"raw": raw, "ts": now_ts()})
        self.dir_text.delete("1.0", tk.END)
        self.log_trace(f"Added directive: {raw}")
        self.refresh_lists()

    def replace_selected(self):
        sel = self.dir_list.curselection()
        if not sel:
            messagebox.showinfo("No selection", "Select a directive to replace.")
            return
        raw = self.dir_text.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("Empty", "Directive text is empty.")
            return
        idx = sel[0]
        old = self.directives[idx]["raw"]
        self.directives[idx] = {"raw": raw, "ts": now_ts()}
        self.log_trace(f"Replaced directive:\n- old: {old}\n- new: {raw}")
        self.refresh_lists()

    def remove_selected(self):
        sel = self.dir_list.curselection()
        if not sel:
            messagebox.showinfo("No selection", "Select a directive to remove.")
            return
        idx = sel[0]
        removed = self.directives.pop(idx)
        self.log_trace(f"Removed directive: {removed['raw']}")
        self.refresh_lists()

    def resolve(self):
        if not self.directives:
            messagebox.showinfo("No directives", "Add directives to resolve.")
            return
        decision = resolve_directives(self.directives, self.ensemble_mode.get())
        self.log_trace(f"[{decision['mode']}] Rationale: " + "; ".join(decision["rationale"]))
        if decision["selected"]:
            for d in decision["selected"]:
                self.log_trace(f"Selected: action={d['action']} target={d.get('target')} priority={d['priority']} safety={d.get('safety')}")
        else:
            self.log_trace("No directive selected. Escalation advised.")
        self.risk_var.set(min(decision["risk_score"], 5.0))

    def escalate(self):
        self.log_trace("Escalation triggered. Pausing execution and deferring to human oversight.")
        messagebox.showinfo("Escalation", "Directive conflict escalated to human oversight for review.")

    def apply_override(self):
        text = self.override_text.get().strip()
        if not text:
            messagebox.showinfo("Empty", "Provide an override rationale or instruction.")
            return
        self.log_trace(f"Manual override applied: {text}")
        messagebox.showinfo("Override", "Manual override recorded. It will take precedence over automated resolution.")

    def clear_trace(self):
        self.trace_text.delete("1.0", tk.END)
        self.trace = []

    def log_trace(self, line):
        entry = f"{now_ts()} | {line}\n"
        self.trace.append(entry)
        self.trace_text.insert(tk.END, entry)
        self.trace_text.see(tk.END)

    def export_state(self):
        payload = {
            "timestamp": now_ts(),
            "ensemble_mode": self.ensemble_mode.get(),
            "directives": self.directives,
            "trace": self.trace,
        }
        try:
            data = json.dumps(payload, indent=2)
            ExportDialog(self, data)
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export: {e}")

class ExportDialog(tk.Toplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title("Export")
        self.geometry("700x500")
        ttk.Label(self, text="Exported JSON").pack(anchor="w", padx=8, pady=6)
        text = tk.Text(self, wrap="none")
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        text.insert("1.0", data)
        text.config(state="disabled")
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=8)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app = AIDirectiveSimulator()
    app.mainloop()

