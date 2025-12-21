#!/usr/bin/env python3
"""
justice_engine.py

Single-file AI-ish justice watchdog:

- Auto-loads optional Python libraries with soft pip install
- Ingests case data from local JSON files
- (Optionally) ingests justice-related data from web APIs / RSS / HTTP sources
- Applies policy rules (pretrial detention, sentencing bounds)
- Scores fairness, consistency, and basic bias patterns
- Emits human-readable and JSON reports
- (Optionally) provides a minimal GUI via Tkinter

Modes:

1) Default GUI mode (if Tkinter available):
   python justice_engine.py

2) Local case file mode (fallback / explicit):
   python justice_engine.py cases.json

3) Web ingest mode (experimental, skeleton):
   python justice_engine.py --web sources_config.json

The goal is not to "judge" but to surface patterns and potential injustices
for human review.
"""

import sys
import subprocess
import importlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import json
import statistics
from datetime import datetime
import os

# ===============================
# 0. Auto-loader for dependencies
# ===============================

AUTOLOADER_LOG: List[str] = []
OPTIONAL_MODULES_STATUS: Dict[str, str] = {}  # "ok", "installed", "failed"


def log_autoloader(msg: str) -> None:
    prefix = "[AutoLoader] "
    line = prefix + msg
    AUTOLOADER_LOG.append(line)
    # Print to stderr to avoid polluting primary outputs
    print(line, file=sys.stderr)


def optional_import(module_name: str, pip_name: Optional[str] = None, installable: bool = True):
    """
    Try to import a module. If it fails and installable=True, attempt to install it via pip
    in the current Python environment, then import again.

    Returns:
        module object if available, else None.
    """
    if pip_name is None:
        pip_name = module_name

    # First attempt: import directly
    try:
        module = importlib.import_module(module_name)
        OPTIONAL_MODULES_STATUS[module_name] = "ok"
        log_autoloader(f"Module '{module_name}' available.")
        return module
    except ImportError:
        if not installable:
            log_autoloader(f"Module '{module_name}' not found and marked non-installable.")
            OPTIONAL_MODULES_STATUS[module_name] = "failed"
            return None
        log_autoloader(f"Module '{module_name}' not found, attempting pip install '{pip_name}'...")

    # Second attempt: pip install in current environment
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log_autoloader(f"pip install '{pip_name}' succeeded, re-importing '{module_name}'...")
        module = importlib.import_module(module_name)
        OPTIONAL_MODULES_STATUS[module_name] = "installed"
        return module
    except Exception as e:
        log_autoloader(f"Failed to install or import '{module_name}': {e}")
        OPTIONAL_MODULES_STATUS[module_name] = "failed"
        return None


def print_autoloader_summary() -> None:
    if not OPTIONAL_MODULES_STATUS:
        return
    print("\n[AutoLoader] Module status summary:", file=sys.stderr)
    for name, status in OPTIONAL_MODULES_STATUS.items():
        print(f"[AutoLoader]  - {name}: {status}", file=sys.stderr)


# Optional web-related dependencies (used in WebIngestor)
requests = optional_import("requests")
feedparser = optional_import("feedparser")

# Optional GUI dependency (Tkinter, non-pip-installable typically)
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    HAVE_TK = True
    OPTIONAL_MODULES_STATUS["tkinter"] = "ok"
    log_autoloader("Module 'tkinter' available for GUI mode.")
except Exception:
    HAVE_TK = False
    OPTIONAL_MODULES_STATUS["tkinter"] = "failed"
    log_autoloader("Module 'tkinter' not available; GUI mode disabled.")


# ===============================
# 1. Config and simple policies
# ===============================

DEFAULT_POLICIES = {
    # Pretrial
    "max_pretrial_detention_days_low_risk": 3,

    # Sentencing bounds
    "max_sentence_misdemeanor_months": 12,
    "max_sentence_nonviolent_felony_years": 5,

    # Fines, if you later add them
    "income_sensitive_fines": True,

    # How extreme differences must be to flag inconsistency
    "flag_if_similar_cases_disparity_factor": 2.0,

    # Bias thresholds (how much harsher vs peers before flagging)
    "bias_ratio_threshold": 1.5,
}

# Example risk categories
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"


# ===============================
# 2. Data models
# ===============================

@dataclass
class Case:
    case_id: str
    charges: List[str]
    severity: str  # e.g., "MISDEMEANOR", "FELONY_NONVIOLENT", "FELONY_VIOLENT"
    prior_record: int  # count of prior convictions
    risk_level: str  # LOW/MEDIUM/HIGH
    defendant_age: int
    defendant_income_level: str  # "LOW", "MID", "HIGH"
    race: Optional[str] = None  # optional, but useful for bias analysis
    judge_id: Optional[str] = None
    prosecutor_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    source: Optional[str] = None  # e.g., "local_file", "web_api", "rss"
    # Ground truth / historical decision
    bail_amount: Optional[float] = None
    pretrial_detention_days: Optional[int] = None
    sentence_months: Optional[int] = None
    diverted: bool = False  # diversion instead of conviction


@dataclass
class PolicyFinding:
    name: str
    passed: bool
    severity: str  # "INFO", "WARNING", "ALERT"
    message: str
    details: Dict[str, Any]


@dataclass
class CaseAnalysis:
    case: Case
    policy_findings: List[PolicyFinding]
    fairness_score: float  # 0-1, 1 = most fair
    consistency_score: float  # 0-1, 1 = consistent with peers
    timestamp: str


# ===============================
# 3. Utility functions
# ===============================

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if b == 0:
        return default
    return a / b


def debug(msg: str) -> None:
    print(f"[JusticeEngine] {msg}", file=sys.stderr)


# ===============================
# 4. Policy checks (per-case)
# ===============================

class PolicyEngine:
    def __init__(self, policies: Dict[str, Any]):
        self.policies = policies

    def check_pretrial_detention(self, case: Case) -> Optional[PolicyFinding]:
        if case.risk_level == RISK_LOW and case.pretrial_detention_days is not None:
            limit = self.policies["max_pretrial_detention_days_low_risk"]
            if case.pretrial_detention_days > limit:
                return PolicyFinding(
                    name="EXCESSIVE_PRETRIAL_DETENTION",
                    passed=False,
                    severity="ALERT",
                    message=(
                        f"Low-risk defendant detained {case.pretrial_detention_days} days "
                        f"(limit {limit})."
                    ),
                    details={
                        "limit": limit,
                        "risk_level": case.risk_level,
                        "jurisdiction": case.jurisdiction,
                    },
                )
        return None

    def check_sentence_length(self, case: Case) -> Optional[PolicyFinding]:
        if case.sentence_months is None:
            return None

        if case.severity == "MISDEMEANOR":
            limit_months = self.policies["max_sentence_misdemeanor_months"]
            if case.sentence_months > limit_months:
                return PolicyFinding(
                    name="EXCESSIVE_SENTENCE_MISDEMEANOR",
                    passed=False,
                    severity="ALERT",
                    message=(
                        f"Misdemeanor sentence {case.sentence_months} months "
                        f"(limit {limit_months})."
                    ),
                    details={
                        "limit_months": limit_months,
                        "jurisdiction": case.jurisdiction,
                    },
                )

        if case.severity == "FELONY_NONVIOLENT":
            limit_years = self.policies["max_sentence_nonviolent_felony_years"]
            limit_months = limit_years * 12
            if case.sentence_months > limit_months:
                return PolicyFinding(
                    name="EXCESSIVE_SENTENCE_NONVIOLENT_FELONY",
                    passed=False,
                    severity="ALERT",
                    message=(
                        f"Nonviolent felony sentence {case.sentence_months} months "
                        f"(limit {limit_months})."
                    ),
                    details={
                        "limit_months": limit_months,
                        "jurisdiction": case.jurisdiction,
                    },
                )

        return None

    def run_all_checks(self, case: Case) -> List[PolicyFinding]:
        findings: List[PolicyFinding] = []

        for fn in [
            self.check_pretrial_detention,
            self.check_sentence_length,
        ]:
            result = fn(case)
            if result is not None:
                findings.append(result)

        return findings


# ===============================
# 5. Fairness & consistency engine
# ===============================

class FairnessEngine:
    """
    Compares a case to peers to see if it's being treated differently.
    For now: simple stats. Later: ML, causal models, etc.
    """

    def __init__(self, historical_cases: List[Case], policies: Dict[str, Any]):
        self.cases = historical_cases
        self.policies = policies

    def _filter_similar_cases(self, target: Case) -> List[Case]:
        return [
            c for c in self.cases
            if c.case_id != target.case_id
            and c.severity == target.severity
            and c.risk_level == target.risk_level
            and abs(c.prior_record - target.prior_record) <= 1
        ]

    def _extract_numeric_outcomes(
        self, cases: List[Case]
    ) -> Dict[str, List[float]]:
        bail = [c.bail_amount for c in cases if c.bail_amount is not None]
        detention = [
            c.pretrial_detention_days for c in cases
            if c.pretrial_detention_days is not None
        ]
        sentence = [
            c.sentence_months for c in cases
            if c.sentence_months is not None
        ]
        return {
            "bail": bail,
            "detention": detention,
            "sentence": sentence,
        }

    def compute_consistency_score(self, target: Case) -> Tuple[float, List[PolicyFinding]]:
        peers = self._filter_similar_cases(target)
        if not peers:
            return 1.0, [
                PolicyFinding(
                    name="NO_PEERS",
                    passed=True,
                    severity="INFO",
                    message="No similar cases to compare for consistency.",
                    details={"case_id": target.case_id},
                )
            ]

        outcomes = self._extract_numeric_outcomes(peers)
        findings: List[PolicyFinding] = []
        disparity_factor = self.policies["flag_if_similar_cases_disparity_factor"]

        def compare(field: str, target_val: Optional[float]):
            if target_val is None or not outcomes[field]:
                return
            peer_median = statistics.median(outcomes[field])
            ratio = max(
                safe_div(target_val, peer_median, 1.0),
                safe_div(peer_median, target_val, 1.0),
            )
            if ratio >= disparity_factor:
                findings.append(
                    PolicyFinding(
                        name=f"INCONSISTENT_{field.upper()}",
                        passed=False,
                        severity="WARNING",
                        message=(
                            f"{field} {target_val} vs peer median {peer_median}, "
                            f"ratio {ratio:.2f} exceeds factor {disparity_factor}."
                        ),
                        details={
                            "field": field,
                            "target_value": target_val,
                            "peer_median": peer_median,
                            "ratio": ratio,
                            "case_id": target.case_id,
                        },
                    )
                )

        compare("bail", target.bail_amount)
        compare("detention", target.pretrial_detention_days)
        compare("sentence", target.sentence_months)

        score = 1.0 if not findings else max(0.0, 1.0 - 0.2 * len(findings))
        return score, findings

    # ---------- basic bias analysis (income + race) ----------

    def _peers_by_group(self, target: Case, group_field: str) -> Dict[str, List[Case]]:
        peers = self._filter_similar_cases(target)
        groups: Dict[str, List[Case]] = {}
        for c in peers:
            key = getattr(c, group_field, None)
            if key is None:
                continue
            groups.setdefault(key, []).append(c)
        return groups

    def _median_outcome(self, cases: List[Case], field: str) -> Optional[float]:
        vals: List[float] = []
        for c in cases:
            v = getattr(c, field, None)
            if v is not None:
                vals.append(v)
        if not vals:
            return None
        return statistics.median(vals)

    def _compare_target_to_group(
        self,
        target: Case,
        group_cases: List[Case],
        field: str,
        label: str,
        ratio_threshold: float,
    ) -> Optional[PolicyFinding]:
        target_val = getattr(target, field, None)
        if target_val is None or not group_cases:
            return None
        group_median = self._median_outcome(group_cases, field)
        if group_median is None:
            return None
        ratio = safe_div(target_val, group_median, 1.0)
        if ratio >= ratio_threshold:
            return PolicyFinding(
                name=f"BIAS_{label.upper()}_{field.upper()}",
                passed=False,
                severity="ALERT",
                message=(
                    f"{label} bias signal on {field}: target {target_val}, "
                    f"group median {group_median}, ratio {ratio:.2f} ≥ {ratio_threshold}."
                ),
                details={
                    "field": field,
                    "target_value": target_val,
                    "group_median": group_median,
                    "ratio": ratio,
                    "case_id": target.case_id,
                    "label": label,
                },
            )
        return None

    def compute_fairness_score(self, target: Case) -> Tuple[float, List[PolicyFinding]]:
        """
        Basic bias analysis:

        - Income bias: is a low-income defendant treated significantly harsher
          than peers with higher income?
        - Race bias: is this race treated significantly harsher than others
          within similar cases?

        This is illustrative; real-world bias analysis is much more complex.
        """
        findings: List[PolicyFinding] = []
        bias_threshold = self.policies.get("bias_ratio_threshold", 1.5)

        base_score = 1.0

        # Income-based bias
        income_groups = self._peers_by_group(target, "defendant_income_level")
        if income_groups and target.defendant_income_level in income_groups:
            income_order = ["LOW", "MID", "HIGH"]
            try:
                target_idx = income_order.index(target.defendant_income_level)
            except ValueError:
                target_idx = None

            if target_idx is not None and target_idx > 0:
                higher_groups: List[Case] = []
                for g in income_order[:target_idx]:
                    higher_groups.extend(income_groups.get(g, []))

                for field in ["bail_amount", "pretrial_detention_days", "sentence_months"]:
                    fnd = self._compare_target_to_group(
                        target,
                        higher_groups,
                        field,
                        label="income",
                        ratio_threshold=bias_threshold,
                    )
                    if fnd is not None:
                        findings.append(fnd)

        # Race-based bias
        race_groups = self._peers_by_group(target, "race")
        if race_groups and target.race is not None:
            other_races_cases: List[Case] = []
            for race_val, group_cases in race_groups.items():
                if race_val != target.race:
                    other_races_cases.extend(group_cases)

            if other_races_cases:
                for field in ["bail_amount", "pretrial_detention_days", "sentence_months"]:
                    fnd = self._compare_target_to_group(
                        target,
                        other_races_cases,
                        field,
                        label="race",
                        ratio_threshold=bias_threshold,
                    )
                    if fnd is not None:
                        findings.append(fnd)

        if not findings:
            base_score = 0.9
        else:
            base_score = max(0.0, 0.9 - 0.1 * len(findings))

        return base_score, findings


# ===============================
# 6. Justice engine (orchestrator)
# ===============================

class JusticeEngine:
    def __init__(
        self,
        policies: Dict[str, Any],
        historical_cases: Optional[List[Case]] = None,
    ):
        self.policies = policies
        self.policy_engine = PolicyEngine(policies)
        self.fairness_engine = FairnessEngine(historical_cases or [], policies)

    def analyze_case(self, case: Case) -> CaseAnalysis:
        policy_findings = self.policy_engine.run_all_checks(case)
        consistency_score, consistency_findings = \
            self.fairness_engine.compute_consistency_score(case)
        fairness_score, fairness_findings = \
            self.fairness_engine.compute_fairness_score(case)

        all_findings = policy_findings + consistency_findings + fairness_findings

        fairness_score = max(0.0, min(1.0, fairness_score))
        consistency_score = max(0.0, min(1.0, consistency_score))

        return CaseAnalysis(
            case=case,
            policy_findings=all_findings,
            fairness_score=fairness_score,
            consistency_score=consistency_score,
            timestamp=now_iso(),
        )


# ===============================
# 7. Web ingestor (experimental)
# ===============================

class WebIngestor:
    """
    Skeleton web ingestor that can read a config describing:
    - RSS feeds
    - Simple HTTP JSON APIs with justice-related data

    It normalizes these into Case objects where possible.
    Real-world mapping will be highly source-specific and
    may require custom mapping logic.
    """

    def __init__(self, sources_config: Dict[str, Any]):
        self.sources_config = sources_config

    def fetch_rss_items(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        rss_sources = self.sources_config.get("rss_feeds", [])
        if not rss_sources:
            return items

        if feedparser is None:
            debug("RSS requested but 'feedparser' is not available. Skipping RSS sources.")
            return items

        for entry in rss_sources:
            url = entry.get("url")
            tag = entry.get("tag", "rss")
            if not url:
                continue
            try:
                debug(f"Fetching RSS feed: {url}")
                feed = feedparser.parse(url)
                for e in feed.entries:
                    items.append({
                        "source_type": "rss",
                        "source_tag": tag,
                        "title": getattr(e, "title", ""),
                        "summary": getattr(e, "summary", ""),
                        "link": getattr(e, "link", ""),
                        "published": getattr(e, "published", None),
                    })
            except Exception as e:
                debug(f"Error fetching/parsing RSS {url}: {e}")
        return items

    def fetch_http_json_items(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        api_sources = self.sources_config.get("http_json_apis", [])
        if not api_sources:
            return items

        if requests is None:
            debug("HTTP JSON APIs requested but 'requests' is not available. Skipping API sources.")
            return items

        for entry in api_sources:
            url = entry.get("url")
            tag = entry.get("tag", "api")
            if not url:
                continue
            try:
                debug(f"Fetching HTTP JSON: {url}")
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                items.append({
                    "source_type": "http_json",
                    "source_tag": tag,
                    "raw": data,
                    "url": url,
                })
            except Exception as e:
                debug(f"Error fetching HTTP JSON {url}: {e}")
        return items

    def fetch_all_raw_items(self) -> List[Dict[str, Any]]:
        raw_items: List[Dict[str, Any]] = []
        raw_items.extend(self.fetch_rss_items())
        raw_items.extend(self.fetch_http_json_items())
        return raw_items

    def map_raw_to_cases(self, raw_items: List[Dict[str, Any]]) -> List[Case]:
        """
        This is intentionally minimal and generic.
        In a real system, you'd define per-source mapping logic.
        For now, we'll:
        - Create synthetic Case IDs
        - Use placeholders for fields we can't infer
        - Mark them as source 'web'
        """
        cases: List[Case] = []
        counter = 1

        for item in raw_items:
            source_type = item.get("source_type", "unknown")
            source_tag = item.get("source_tag", "web")
            base_id = f"WEB_{source_tag.upper()}_{counter}"
            counter += 1

            severity = "MISDEMEANOR"
            risk_level = RISK_LOW
            prior_record = 0
            sentence_months = None
            bail_amount = None
            pretrial_days = None
            jurisdiction = None

            if source_type == "http_json":
                raw = item.get("raw", {})
                severity = raw.get("severity", severity)
                risk_level = raw.get("risk_level", risk_level)
                try:
                    prior_record = int(raw.get("prior_record", prior_record))
                except Exception:
                    pass
                sentence_months = raw.get("sentence_months", sentence_months)
                bail_amount = raw.get("bail_amount", bail_amount)
                pretrial_days = raw.get("pretrial_detention_days", pretrial_days)
                jurisdiction = raw.get("jurisdiction", jurisdiction)

            case = Case(
                case_id=base_id,
                charges=["UNKNOWN_CHARGE"],
                severity=severity,
                prior_record=prior_record,
                risk_level=risk_level,
                defendant_age=30,
                defendant_income_level="MID",
                race=None,
                judge_id=None,
                prosecutor_id=None,
                jurisdiction=jurisdiction,
                source=source_type,
                bail_amount=bail_amount,
                pretrial_detention_days=pretrial_days,
                sentence_months=sentence_months,
                diverted=False,
            )
            cases.append(case)

        return cases


# ===============================
# 8. I/O helpers and reporting
# ===============================

def case_from_dict(d: Dict[str, Any]) -> Case:
    return Case(**d)


def load_cases_from_json(path: str) -> List[Case]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict) and "cases" in raw:
        raw_cases = raw["cases"]
    else:
        raw_cases = raw
    cases: List[Case] = []
    for c in raw_cases:
        d = dict(c)
        d.setdefault("source", "local_file")
        cases.append(case_from_dict(d))
    return cases


def analysis_to_dict(analysis: CaseAnalysis) -> Dict[str, Any]:
    return {
        "case": asdict(analysis.case),
        "fairness_score": analysis.fairness_score,
        "consistency_score": analysis.consistency_score,
        "timestamp": analysis.timestamp,
        "policy_findings": [asdict(f) for f in analysis.policy_findings],
    }


def format_human_report(analysis: CaseAnalysis) -> str:
    c = analysis.case
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f"Case {c.case_id} analysis at {analysis.timestamp}")
    lines.append("-" * 80)
    lines.append(f"Source: {c.source}, Jurisdiction: {c.jurisdiction}")
    lines.append(f"Severity: {c.severity}, Risk: {c.risk_level}, Prior record: {c.prior_record}")
    lines.append(f"Income level: {c.defendant_income_level}, Race: {c.race}")
    lines.append(
        f"Sentence (months): {c.sentence_months}, Bail: {c.bail_amount}, "
        f"Pretrial detention (days): {c.pretrial_detention_days}"
    )
    lines.append(f"Diversion: {c.diverted}")
    lines.append("")
    lines.append(f"Fairness score:    {analysis.fairness_score:.2f}")
    lines.append(f"Consistency score: {analysis.consistency_score:.2f}")
    lines.append("")
    if not analysis.policy_findings:
        lines.append("No policy, consistency, or bias issues found.")
    else:
        lines.append("Findings:")
        for f in analysis.policy_findings:
            status = "PASS" if f.passed else "FAIL"
            lines.append(f" - [{status}] {f.severity}: {f.name}")
            lines.append(f"   {f.message}")
            if f.details:
                lines.append(f"   details: {f.details}")
    lines.append("=" * 80)
    return "\n".join(lines)


def print_human_report(analysis: CaseAnalysis) -> None:
    print(format_human_report(analysis))


# ===============================
# 9. CLI modes (local, web)
# ===============================

def run_local_mode(cases_path: str) -> None:
    debug(f"Running local mode with cases file: {cases_path}")
    cases = load_cases_from_json(cases_path)

    if not cases:
        print("No cases found.")
        return

    engine = JusticeEngine(DEFAULT_POLICIES, historical_cases=cases)

    all_results: List[Dict[str, Any]] = []
    for c in cases:
        analysis = engine.analyze_case(c)
        print_human_report(analysis)
        all_results.append(analysis_to_dict(analysis))

    base, ext = os.path.splitext(cases_path)
    out_path = base + "_analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"analyses": all_results}, f, indent=2)

    print(f"\nAnalysis written to {out_path}")
    print_autoloader_summary()


def load_sources_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_web_mode(config_path: str) -> None:
    debug(f"Running web mode with sources config: {config_path}")
    cfg = load_sources_config(config_path)
    ingestor = WebIngestor(cfg)
    raw_items = ingestor.fetch_all_raw_items()
    debug(f"Fetched {len(raw_items)} raw web items.")
    cases = ingestor.map_raw_to_cases(raw_items)
    debug(f"Mapped {len(cases)} items into Case objects.")

    if not cases:
        print("No cases derived from web sources.")
        print_autoloader_summary()
        return

    engine = JusticeEngine(DEFAULT_POLICIES, historical_cases=cases)

    all_results: List[Dict[str, Any]] = []
    for c in cases:
        analysis = engine.analyze_case(c)
        print_human_report(analysis)
        all_results.append(analysis_to_dict(analysis))

    base, ext = os.path.splitext(config_path)
    out_path = base + "_web_analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"analyses": all_results}, f, indent=2)

    print(f"\nWeb analysis written to {out_path}")
    print_autoloader_summary()


# ===============================
# 10. GUI mode (if Tkinter available)
# ===============================

class JusticeGUI:
    def __init__(self, root: "tk.Tk"):
        self.root = root
        self.root.title("Justice Engine Watchdog")
        self.engine: Optional[JusticeEngine] = None

        # Layout
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill=tk.X, padx=5, pady=5)

        self.btn_open = tk.Button(self.frame_top, text="Open cases.json", command=self.open_cases)
        self.btn_open.pack(side=tk.LEFT, padx=5)

        self.btn_analyze = tk.Button(self.frame_top, text="Analyze", command=self.run_analysis, state=tk.DISABLED)
        self.btn_analyze.pack(side=tk.LEFT, padx=5)

        self.lbl_status = tk.Label(self.frame_top, text="No file loaded.")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.text_output = tk.Text(root, wrap=tk.NONE, height=30)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.scroll_y = tk.Scrollbar(self.text_output, orient=tk.VERTICAL, command=self.text_output.yview)
        self.text_output.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.cases: List[Case] = []
        self.cases_path: Optional[str] = None

    def open_cases(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select cases.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            self.cases = load_cases_from_json(filename)
            if not self.cases:
                messagebox.showwarning("Justice Engine", "No cases found in file.")
                return
            self.engine = JusticeEngine(DEFAULT_POLICIES, historical_cases=self.cases)
            self.cases_path = filename
            self.lbl_status.config(text=f"Loaded {len(self.cases)} cases from {os.path.basename(filename)}")
            self.btn_analyze.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Justice Engine", f"Error loading cases: {e}")

    def run_analysis(self) -> None:
        if not self.cases or self.engine is None:
            messagebox.showwarning("Justice Engine", "No cases loaded.")
            return

        self.text_output.delete("1.0", tk.END)
        all_results: List[Dict[str, Any]] = []

        for c in self.cases:
            analysis = self.engine.analyze_case(c)
            report = format_human_report(analysis)
            self.text_output.insert(tk.END, report + "\n")
            all_results.append(analysis_to_dict(analysis))

        # Also write JSON summary next to the file if we know it
        if self.cases_path:
            base, ext = os.path.splitext(self.cases_path)
            out_path = base + "_analysis.json"
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump({"analyses": all_results}, f, indent=2)
                self.text_output.insert(tk.END, f"\nAnalysis written to {out_path}\n")
            except Exception as e:
                self.text_output.insert(tk.END, f"\nError writing analysis file: {e}\n")


def run_gui_mode() -> None:
    if not HAVE_TK:
        print("Tkinter is not available; GUI mode cannot be started.")
        print_autoloader_summary()
        return
    root = tk.Tk()
    app = JusticeGUI(root)
    root.mainloop()
    print_autoloader_summary()


# ===============================
# 11. Usage and main
# ===============================

def print_usage() -> None:
    print("Usage:")
    print("  Default GUI mode (if Tkinter available):")
    print("    python justice_engine.py")
    print()
    print("  Local cases file mode (CLI fallback):")
    print("    python justice_engine.py cases.json")
    print()
    print("  Web ingest mode (experimental):")
    print("    python justice_engine.py --web sources_config.json")
    print()
    print("cases.json format example:")
    print('''
{
  "cases": [
    {
      "case_id": "C1",
      "charges": ["THEFT"],
      "severity": "MISDEMEANOR",
      "prior_record": 0,
      "risk_level": "LOW",
      "defendant_age": 23,
      "defendant_income_level": "LOW",
      "race": "A",
      "judge_id": "J1",
      "prosecutor_id": "P1",
      "jurisdiction": "ExampleState",
      "bail_amount": 500.0,
      "pretrial_detention_days": 5,
      "sentence_months": 2,
      "diverted": false,
      "source": "local_file"
    }
  ]
}
''')
    print("sources_config.json example:")
    print('''
{
  "rss_feeds": [
    {
      "url": "https://example.org/justice-news-rss",
      "tag": "justice_news"
    }
  ],
  "http_json_apis": [
    {
      "url": "https://example.org/api/justice-cases",
      "tag": "public_cases"
    }
  ]
}
''')


def main(argv: List[str]) -> None:
    # Default behavior: if Tkinter is available, launch GUI directly.
    if HAVE_TK and (len(argv) == 1 or (len(argv) == 2 and argv[1] == "--gui")):
        run_gui_mode()
        return

    # If Tkinter not available, or explicit CLI/web usage
    if len(argv) < 2:
        print("Tkinter not available or no arguments provided. Falling back to CLI usage.")
        print_usage()
        return

    if argv[1] == "--web":
        if len(argv) < 3:
            print("Missing sources_config.json for --web mode.")
            return
        config_path = argv[2]
        run_web_mode(config_path)
    else:
        cases_path = argv[1]
        run_local_mode(cases_path)


if __name__ == "__main__":
    main(sys.argv)

