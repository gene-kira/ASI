#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Prometheus Scanner (System + External + Missing Link)
- Full single-file script, GUI scaled ~50% smaller
- System telemetry (CPU/GPU/RAM/Disk/Net/Processes/Ports/Connections)
- Autonomous external scans (HTTP ping, DNS, port checks)
- Autonomous Missing Link inference + AI Brain simulations
- Technical GUI (tkinter) with dashboards, Completed tab (scrollable), and audit console
"""

import sys, subprocess, threading, time, math, itertools, random, json, socket, queue
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional, Callable

# ---------------------------
# Auto-loader
# ---------------------------

AUTOLOAD_LOG = []

def autoload(package: str, import_name: Optional[str] = None):
    name = import_name or package
    try:
        mod = __import__(name)
        AUTOLOAD_LOG.append(f"[autoload] {name} available.")
        return mod
    except ImportError:
        AUTOLOAD_LOG.append(f"[autoload] {name} missing. Installing '{package}' via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            mod = __import__(name)
            AUTOLOAD_LOG.append(f"[autoload] {name} installed and imported.")
            return mod
        except Exception as e:
            AUTOLOAD_LOG.append(f"[autoload] Failed to install '{package}': {e}")
            return None

psutil = autoload("psutil")
GPUtil = autoload("GPUtil")
pynvml = autoload("pynvml")

# tkinter
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception as e:
    raise RuntimeError("tkinter is required for the GUI.") from e

# ---------------------------
# Thread-safe log bus
# ---------------------------

class LogBus:
    def __init__(self):
        self.q = queue.Queue()

    def put(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.q.put(f"[{ts}] {msg}")

    def get_all(self) -> List[str]:
        out = []
        while True:
            try:
                out.append(self.q.get_nowait())
            except queue.Empty:
                break
        return out

LOG_BUS = LogBus()

# ---------------------------
# Puzzle core (pieces, constraints, recognizer, scanner, missing link, AI brain)
# ---------------------------

@dataclass
class Piece:
    id: str
    attrs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    a: str
    b: str
    relation: str = "linked"
    weight: float = 1.0

@dataclass
class Constraint:
    name: str
    fn: Callable[[Dict[str, Piece], Dict[str, Any]], Tuple[bool, str]]
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Puzzle:
    pieces: Dict[str, Piece] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)

    def add_piece(self, pid: str, **attrs):
        if pid in self.pieces:
            raise ValueError(f"Piece '{pid}' already exists.")
        self.pieces[pid] = Piece(pid, attrs)

    def set_attr(self, pid: str, key: str, value: Any):
        if pid not in self.pieces:
            raise ValueError(f"Unknown piece '{pid}'.")
        self.pieces[pid].attrs[key] = value

    def add_edge(self, a: str, b: str, relation: str = "linked", weight: float = 1.0):
        if a not in self.pieces or b not in self.pieces:
            raise ValueError("Edges require existing pieces.")
        self.edges.append(Edge(a, b, relation, weight))

    def add_constraint(self, name: str, fn: Callable[[Dict[str, Piece], Dict[str, Any]], Tuple[bool, str]], **params):
        self.constraints.append(Constraint(name, fn, params))

    def evaluate_constraints(self) -> Tuple[bool, List[str]]:
        msgs = []
        ok = True
        for c in self.constraints:
            res, msg = c.fn(self.pieces, c.params)
            if not res:
                ok = False
            msgs.append(f"[{c.name}] {msg}")
        return ok, msgs

class PatternRecognizer:
    def __init__(self, pieces: Dict[str, Piece], edges: List[Edge]):
        self.pieces = pieces
        self.edges = edges

    def _numeric_attrs(self) -> Dict[str, Dict[str, float]]:
        out = {}
        for pid, p in self.pieces.items():
            num = {}
            for k, v in p.attrs.items():
                if isinstance(v, (int, float)):
                    num[k] = float(v)
            out[pid] = num
        return out

    def cluster_numeric(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        data = self._numeric_attrs()
        if keys is None:
            keys = sorted({k for num in data.values() for k in num.keys()})
        if not keys:
            return {"centroid": {}, "distances": {}, "outliers": []}
        centroid = {k: 0.0 for k in keys}
        n = 0
        for num in data.values():
            if all(k in num for k in keys):
                for k in keys:
                    centroid[k] += num[k]
                n += 1
        if n > 0:
            for k in keys:
                centroid[k] /= n
        distances = {}
        for pid, num in data.items():
            if all(k in num for k in keys) and n > 0:
                d = math.sqrt(sum((num[k] - centroid[k]) ** 2 for k in keys))
                distances[pid] = d
        vals = list(distances.values())
        if vals:
            mu = sum(vals)/len(vals)
            std = math.sqrt(sum((v - mu) ** 2 for v in vals) / max(1, len(vals)))
            thresh = mu + 1.5 * std
            outliers = [pid for pid, d in distances.items() if d > thresh]
        else:
            outliers = []
        return {"centroid": centroid, "distances": distances, "outliers": outliers}

    def motif_frequency(self) -> Dict[str, int]:
        freq = {}
        for e in self.edges:
            freq[e.relation] = freq.get(e.relation, 0) + 1
        return freq

    def hypothesize_links(self) -> List[Dict[str, Any]]:
        deg = {}
        for e in self.edges:
            deg[e.a] = deg.get(e.a, 0) + 1
            deg[e.b] = deg.get(e.b, 0) + 1
        hyps = []
        cl = self.cluster_numeric(keys=sorted({k for num in self._numeric_attrs().values() for k in num.keys()}))
        centroid = cl["centroid"]
        for pid, p in self.pieces.items():
            d = deg.get(pid, 0)
            richness = len(p.attrs)
            score = max(0.1, richness) / (d + 0.5)
            target = None
            if centroid:
                best = None
                best_d = float("inf")
                for qid, num in self._numeric_attrs().items():
                    if qid == pid: continue
                    if all(k in num for k in centroid.keys()):
                        dd = math.sqrt(sum((num[k]-centroid[k])**2 for k in centroid.keys()))
                        if dd < best_d: best_d, best = dd, qid
                target = best
            hyps.append({"piece": pid, "suggested_target": target, "score": round(score,3), "reason": "Rich attrs; low degree; link towards centroid."})
        hyps.sort(key=lambda h: h["score"], reverse=True)
        return hyps

class MissingLink:
    def __init__(self, domain_generators: Dict[str, Callable[[], List[Any]]]):
        self.domain_generators = domain_generators

    def infer(self, formula: Callable[[Dict[str, Any]], bool], partial: Dict[str, Any],
              unknowns: List[str], limit: int = 20000) -> Dict[str, Any]:
        domains = {u: self.domain_generators[u]() if u in self.domain_generators else [] for u in unknowns}
        for u, dom in domains.items():
            if not dom:
                raise ValueError(f"No domain candidates for unknown '{u}'.")
        results, count = [], 0
        start = time.time()
        for combo in itertools.product(*[domains[u] for u in unknowns]):
            assign = dict(partial)
            for u, v in zip(unknowns, combo):
                assign[u] = v
            try:
                ok = formula(assign)
            except Exception:
                ok = False
            if ok:
                results.append({"assignment": assign.copy(), "source": "missing_link"})
            count += 1
            if count >= limit:
                break
        scores = []
        for r in results:
            s = 0.0
            for u, dom in domains.items():
                try:
                    idx = dom.index(r["assignment"][u])
                    center = (len(dom)-1)/2.0
                    s += 1.0 - abs(idx-center)/max(1.0, center)
                except Exception:
                    s += 0.5
            scores.append(s/max(1, len(unknowns)))
        ranked = [{"assignment": r["assignment"], "score": round(s,3), "source": r["source"]} for r, s in zip(results, scores)]
        ranked.sort(key=lambda x: x["score"], reverse=True)
        duration = round(time.time()-start, 3)
        return {"unknowns": unknowns, "solutions": ranked, "Searched": count, "duration_s": duration}

@dataclass
class ScanLayer:
    name: str
    notes: List[str]
    findings: Dict[str, Any]

class PrometheusScanner:
    def __init__(self, puzzle: Puzzle, recognizer: PatternRecognizer):
        self.puzzle = puzzle
        self.recognizer = recognizer
        self.layers: List[ScanLayer] = []

    def pass_topology(self):
        deg = {}
        for e in self.puzzle.edges:
            deg[e.a] = deg.get(e.a, 0)+1
            deg[e.b] = deg.get(e.b, 0)+1
        hubs = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:3]
        isolates = [pid for pid in self.puzzle.pieces if deg.get(pid,0)==0]
        self.layers.append(ScanLayer("Topology", [f"Hubs: {hubs}", f"Isolates: {isolates}"], {"degree": deg}))

    def pass_constraints(self):
        ok, msgs = self.puzzle.evaluate_constraints()
        self.layers.append(ScanLayer("Constraints", msgs, {"ok": ok}))

    def pass_patterns(self):
        cl = self.recognizer.cluster_numeric()
        motifs = self.recognizer.motif_frequency()
        hyps = self.recognizer.hypothesize_links()
        self.layers.append(ScanLayer("Patterns", [
            f"Centroid: {cl['centroid']}",
            f"Outliers: {cl['outliers']}",
            f"Motifs: {motifs}",
            f"Hypotheses(top5): {[{'piece':h['piece'],'target':h['suggested_target'],'score':h['score']} for h in hyps[:5]]}"
        ], {"cluster": cl, "motifs": motifs, "hypotheses": hyps}))

    def pass_counterfactuals(self, samples: int = 3):
        hyps = self.recognizer.hypothesize_links()
        trials = []
        for h in hyps[:samples]:
            pid, tgt = h["piece"], h["suggested_target"]
            if not tgt: continue
            ok_before, _ = self.puzzle.evaluate_constraints()
            self.puzzle.add_edge(pid, tgt, relation="hypo", weight=0.5)
            ok_after, msgs_after = self.puzzle.evaluate_constraints()
            trials.append({"add": (pid, tgt), "ok_before": ok_before, "ok_after": ok_after, "delta": int(ok_after)-int(ok_before), "notes_after": msgs_after})
            self.puzzle.edges.pop()
        self.layers.append(ScanLayer("Counterfactuals", [f"Trials: {trials}"], {"trials": trials}))

    def scan(self):
        self.layers.clear()
        self.pass_topology()
        self.pass_constraints()
        self.pass_patterns()
        self.pass_counterfactuals()

    def cave_map(self) -> str:
        deg = {}
        for e in self.puzzle.edges:
            deg[e.a] = deg.get(e.a,0)+1
            deg[e.b] = deg.get(e.b,0)+1
        cl = self.recognizer.cluster_numeric()
        outliers = set(cl["outliers"])
        hyps = self.recognizer.hypothesize_links()
        hot = {h["piece"] for h in hyps[:max(3, len(hyps)//3)]}
        lines = ["== Cave Map =="]
        for pid, p in sorted(self.puzzle.pieces.items()):
            tunnels = deg.get(pid, 0)
            known = [f"{k}:{v}" for k, v in p.attrs.items()]
            expected = set(cl["centroid"].keys())
            missing = [k for k in expected if k not in p.attrs]
            marks = []
            if known: marks.append("K")
            if missing: marks.append("M")
            if pid in outliers: marks.append("O")
            if pid in hot: marks.append("H")
            lines.append(f"{pid:>8} | deg={tunnels:<2} | attrs=[{', '.join(known)}] | missing={missing} | marks={' '.join(marks)}")
        return "\n".join(lines)

    def report(self) -> Dict[str, Any]:
        return {"layers": [{"name": l.name, "notes": l.notes, "findings": l.findings} for l in self.layers], "map": self.cave_map()}

# Constraints
def constraint_sum_equals(pieces: Dict[str, Piece], params: Dict[str, Any]) -> Tuple[bool, str]:
    ids, attr, target = params.get("pieces", []), params.get("attr",""), params.get("target", 0.0)
    total, missing = 0.0, []
    for pid in ids:
        v = pieces.get(pid, Piece(pid)).attrs.get(attr)
        if v is None: missing.append(pid)
        else: total += float(v)
    ok = (not missing) and abs(total - float(target)) < 1e-9
    msg = f"sum({attr} over {ids}) == {target} | total={total} | missing={missing}"
    return ok, msg

def constraint_difference_matches(pieces: Dict[str, Piece], params: Dict[str, Any]) -> Tuple[bool, str]:
    a, b, attr, target = params.get("a"), params.get("b"), params.get("attr",""), params.get("target",0.0)
    va = pieces.get(a, Piece(a)).attrs.get(attr)
    vb = pieces.get(b, Piece(b)).attrs.get(attr)
    missing = [x for x, v in [(a, va), (b, vb)] if v is None]
    ok = (not missing) and abs(float(va) - float(vb) - float(target)) < 1e-9
    msg = f"diff({a}.{attr} - {b}.{attr}) == {target} | values=({va},{vb}) | missing={missing}"
    return ok, msg

# AI Brain
class AIBrain:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        random.seed(42)

    def _constraints_ok(self, assign: Dict[str, Any]) -> bool:
        snapshot = {}
        for pid, kv in assign.items():
            piece = self.puzzle.pieces.get(pid)
            if piece:
                snapshot[pid] = piece.attrs.copy()
                piece.attrs.update({"value": kv} if not isinstance(kv, dict) else kv)
        ok, _ = self.puzzle.evaluate_constraints()
        for pid, attrs in snapshot.items():
            self.puzzle.pieces[pid].attrs = attrs
        return ok

    def propose(self, unknowns: Dict[str, List[Any]], fitness: Callable[[Dict[str, Any]], float], budget: int = 8000) -> List[Dict[str, Any]]:
        pruned = {u: [] for u in unknowns}
        for u, dom in unknowns.items():
            for v in dom:
                if self._constraints_ok({u: v}):
                    pruned[u].append(v)
        for u in pruned:
            if not pruned[u]:
                pruned[u] = unknowns[u][:]

        samples, mc_budget = [], budget//3
        for _ in range(mc_budget):
            assign = {u: random.choice(dom) for u, dom in pruned.items()}
            if self._constraints_ok(assign):
                samples.append({"assignment": assign.copy(), "score": fitness(assign), "source": "ai_brain:mc"})

        population = samples[:max(10, len(samples)//2)] or [{"assignment": {u: random.choice(dom) for u, dom in pruned.items()}, "score": fitness({u: random.choice(dom) for u, dom in pruned.items()}), "source": "ai_brain:init"}]
        for _ in range(budget - mc_budget):
            if not population: break
            parent = random.choice(population)
            child = {"assignment": dict(parent["assignment"]), "score": parent["score"], "source": "ai_brain:evo"}
            for u, dom in pruned.items():
                if dom and isinstance(dom[0], (int, float)) and random.random() < 0.6:
                    mu = sum(dom)/len(dom)
                    choice = min(dom, key=lambda x: abs(x - mu + random.uniform(-0.3, 0.3)))
                    child["assignment"][u] = choice
                elif dom:
                    child["assignment"][u] = random.choice(dom)
            if self._constraints_ok(child["assignment"]):
                child["score"] = fitness(child["assignment"])
                population.append(child)

        ranked = sorted(population, key=lambda x: x["score"], reverse=True)
        out, seen = [], set()
        for r in ranked:
            key = json.dumps(r["assignment"], sort_keys=True)
            if key in seen: continue
            seen.add(key)
            out.append(r)
            if len(out) >= 50: break
        return out

# ---------------------------
# System telemetry, ports, and external probes
# ---------------------------

@dataclass
class TelemetrySnapshot:
    ts: float
    cpu_percent: float
    cpu_per_core: List[float]
    ram_used_mb: float
    ram_total_mb: float
    disk_used_mb: float
    disk_total_mb: float
    net_bytes_sent: float
    net_bytes_recv: float
    gpu_info: List[Dict[str, Any]]
    top_procs: List[Dict[str, Any]]
    ports_listening: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    conn_counts: Dict[str, int]

class SystemMonitor:
    def __init__(self, interval_s: float = 1.0):
        self.interval_s = interval_s
        self.snapshots: List[TelemetrySnapshot] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        info = []
        try:
            if GPUtil:
                gpus = GPUtil.getGPUs()
                for g in gpus:
                    info.append({
                        "id": g.id, "name": g.name,
                        "load": round(g.load*100, 1),
                        "mem_used_mb": round(g.memoryUsed, 1),
                        "mem_total_mb": round(g.memoryTotal, 1),
                        "temp_c": getattr(g, "temperature", None) or 0.0
                    })
            elif pynvml:
                try:
                    pynvml.nvmlInit()
                    count = pynvml.nvmlDeviceGetCount()
                    for i in range(count):
                        h = pynvml.nvmlDeviceGetHandleByIndex(i)
                        name = pynvml.nvmlDeviceGetName(h).decode()
                        mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                        util = pynvml.nvmlDeviceGetUtilizationRates(h)
                        temp = pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU)
                        info.append({
                            "id": i, "name": name,
                            "load": util.gpu,
                            "mem_used_mb": round(mem.used/1024/1024,1),
                            "mem_total_mb": round(mem.total/1024/1024,1),
                            "temp_c": temp
                        })
                finally:
                    pynvml.nvmlShutdown()
        except Exception:
            pass
        return info

    def _top_processes(self, n: int = 8) -> List[Dict[str, Any]]:
        procs = []
        try:
            for p in psutil.process_iter(attrs=["pid","name","cpu_percent","memory_info"]):
                mem_mb = (p.info["memory_info"].rss/1024/1024) if p.info.get("memory_info") else 0
                procs.append({"pid": p.info["pid"], "name": p.info["name"], "cpu": p.info["cpu_percent"], "mem_mb": round(mem_mb, 1)})
            procs.sort(key=lambda x: (x["cpu"], x["mem_mb"]), reverse=True)
        except Exception:
            pass
        return procs[:n]

    def _ports_and_connections(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
        listening = []
        conns_out = []
        counts = {"TCP_ESTABLISHED": 0, "TCP_LISTEN": 0, "TCP_OTHER": 0, "UDP": 0}
        try:
            for c in psutil.net_connections(kind='inet'):
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
                raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
                entry = {
                    "type": c.type,
                    "family": c.family,
                    "status": c.status,
                    "laddr": laddr,
                    "raddr": raddr,
                    "pid": c.pid
                }
                if c.type == socket.SOCK_STREAM:
                    if c.status == psutil.CONN_LISTEN:
                        counts["TCP_LISTEN"] += 1
                        listening.append(entry)
                    else:
                        conns_out.append(entry)
                        if c.status == psutil.CONN_ESTABLISHED:
                            counts["TCP_ESTABLISHED"] += 1
                        else:
                            counts["TCP_OTHER"] += 1
                elif c.type == socket.SOCK_DGRAM:
                    counts["UDP"] += 1
                    if not raddr:
                        listening.append(entry)
                    else:
                        conns_out.append(entry)
        except Exception:
            pass
        return listening, conns_out, counts

    def poll_once(self):
        if not psutil:
            return
        cpu_perc = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/") if hasattr(psutil, "disk_usage") else None
        net = psutil.net_io_counters() if hasattr(psutil, "net_io_counters") else None
        listening, conns_out, counts = self._ports_and_connections()
        snap = TelemetrySnapshot(
            ts=time.time(),
            cpu_percent=cpu_perc,
            cpu_per_core=cpu_cores,
            ram_used_mb=round(vm.used/1024/1024,1),
            ram_total_mb=round(vm.total/1024/1024,1),
            disk_used_mb=round((disk.used/1024/1024) if disk else 0,1),
            disk_total_mb=round((disk.total/1024/1024) if disk else 0,1),
            net_bytes_sent=(net.bytes_sent if net else 0),
            net_bytes_recv=(net.bytes_recv if net else 0),
            gpu_info=self._get_gpu_info(),
            top_procs=self._top_processes(),
            ports_listening=listening,
            connections=conns_out,
            conn_counts=counts
        )
        self.snapshots.append(snap)
        if len(self.snapshots) > 600:
            self.snapshots.pop(0)

    def start(self):
        if self.running: return
        self.running = True
        def loop():
            while self.running:
                self.poll_once()
                time.sleep(self.interval_s)
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

# External probes
class ExternalProbe:
    def http_ping(self, host: str, timeout_s: float = 2.0) -> Dict[str, Any]:
        import urllib.request
        start = time.time()
        try:
            with urllib.request.urlopen(host, timeout=timeout_s) as resp:
                dur = round(time.time()-start,3)
                return {"host": host, "status": resp.status, "time_s": dur}
        except Exception as e:
            dur = round(time.time()-start,3)
            return {"host": host, "error": str(e), "time_s": dur}

    def dns_lookup(self, name: str) -> Dict[str, Any]:
        try:
            ip = socket.gethostbyname(name)
            return {"name": name, "ip": ip}
        except Exception as e:
            return {"name": name, "error": str(e)}

    def port_check(self, host: str, port: int, timeout_s: float = 1.5) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_s)
        start = time.time()
        try:
            s.connect((host, port))
            s.close()
            return {"host": host, "port": port, "open": True, "time_s": round(time.time()-start,3)}
        except Exception as e:
            return {"host": host, "port": port, "open": False, "error": str(e), "time_s": round(time.time()-start,3)}

# ---------------------------
# Demo puzzle setup
# ---------------------------

def demo_puzzle() -> Tuple[Puzzle, PrometheusScanner, MissingLink, AIBrain]:
    puzzle = Puzzle()
    for pid in ["A","B","C","D","E"]:
        puzzle.add_piece(pid)
    puzzle.set_attr("A","value",4)
    puzzle.set_attr("B","value",7)
    puzzle.set_attr("C","value",9)
    puzzle.add_edge("A","B", relation="adjacent", weight=1.2)
    puzzle.add_edge("B","C", relation="adjacent", weight=1.0)
    puzzle.add_constraint("sum_ABC_D", constraint_sum_equals, pieces=["A","B","C","D"], attr="value", target=30)
    puzzle.add_constraint("diff_CB_2", constraint_difference_matches, a="C", b="B", attr="value", target=2)

    recognizer = PatternRecognizer(puzzle.pieces, puzzle.edges)

    def gen_D():
        vals = [puzzle.pieces[x].attrs.get("value") for x in ["A","B","C"]]
        base = [v for v in vals if isinstance(v, (int, float))]
        mu = (sum(base)/len(base)) if base else 10
        return sorted(set(int(mu + d) for d in range(-30, 31)))

    def gen_E():
        return ["alpha","beta","gamma","delta","epsilon"]

    missing = MissingLink(domain_generators={"D": gen_D, "E": gen_E})
    scanner = PrometheusScanner(puzzle, recognizer)
    brain = AIBrain(puzzle)
    return puzzle, scanner, missing, brain

# ---------------------------
# Autonomous managers
# ---------------------------

class ExternalAutonomousScanner:
    """
    Periodically performs HTTP pings, DNS lookups, and port checks on safe default endpoints.
    Logs all results to LOG_BUS and Completed tab. Runs non-stop in background.
    """
    def __init__(self, prober: ExternalProbe, interval_s: float = 5.0):
        self.prober = prober
        self.interval_s = interval_s
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.targets_http = ["https://example.com", "https://www.google.com", "https://www.wikipedia.org"]
        self.targets_dns = ["example.com", "google.com", "wikipedia.org", "localhost"]
        self.targets_ports = [("example.com", 80), ("example.com", 443), ("localhost", 22), ("localhost", 80)]

    def start(self):
        if self.running: return
        self.running = True
        def loop():
            idx = 0
            while self.running:
                try:
                    url = self.targets_http[idx % len(self.targets_http)]
                    res = self.prober.http_ping(url)
                    LOG_BUS.put(f"HTTP ping {url} => {res}")
                    name = self.targets_dns[idx % len(self.targets_dns)]
                    dns = self.prober.dns_lookup(name)
                    LOG_BUS.put(f"DNS lookup {name} => {dns}")
                    host, port = self.targets_ports[idx % len(self.targets_ports)]
                    port_res = self.prober.port_check(host, port)
                    LOG_BUS.put(f"Port check {host}:{port} => {port_res}")
                    idx += 1
                except Exception as e:
                    LOG_BUS.put(f"[external] error: {e}")
                time.sleep(self.interval_s)
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

class MissingLinkAutonomy:
    """
    Periodically scans puzzle for unknown 'value' attributes, runs AI Brain proposals,
    and applies the top candidate automatically. Logs all actions and writes to Completed tab.
    """
    def __init__(self, puzzle: Puzzle, brain: AIBrain, interval_s: float = 7.0):
        self.puzzle = puzzle
        self.brain = brain
        self.interval_s = interval_s
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        if self.running: return
        self.running = True
        def loop():
            while self.running:
                try:
                    unknowns = {}
                    vals = [p.attrs.get("value") for p in self.puzzle.pieces.values() if isinstance(p.attrs.get("value"), (int, float))]
                    mu = (sum(vals)/len(vals)) if vals else 10
                    dom_proto = [int(mu + d) for d in range(-80, 81)]
                    for pid, piece in self.puzzle.pieces.items():
                        if "value" not in piece.attrs:
                            unknowns[pid] = dom_proto[:]
                    if unknowns:
                        recognizer = PatternRecognizer(self.puzzle.pieces, self.puzzle.edges)
                        cl = recognizer.cluster_numeric()
                        centroid = cl.get("centroid", {})
                        def fitness(assign: Dict[str, Any]) -> float:
                            score = 0.0
                            ok = self.brain._constraints_ok(assign)
                            score += 10.0 if ok else -3.0
                            muv = centroid.get("value", mu)
                            for u, v in assign.items():
                                if isinstance(v, (int, float)):
                                    score += max(0.0, 3.0 - abs(v - muv) * 0.15)
                            score += len(assign) * 0.1
                            return score
                        proposals = self.brain.propose(unknowns, fitness=fitness, budget=10000)
                        if proposals:
                            best = proposals[0]["assignment"]
                            for u, v in best.items():
                                try:
                                    self.puzzle.set_attr(u, "value", v)
                                except Exception:
                                    pass
                            LOG_BUS.put(f"[Completed] MissingLinkAutonomy applied proposal: {best}")
                        else:
                            LOG_BUS.put("MissingLinkAutonomy: no viable proposals.")
                    else:
                        LOG_BUS.put("MissingLinkAutonomy: no unknowns detected.")
                except Exception as e:
                    LOG_BUS.put(f"[missing_link] error: {e}")
                time.sleep(self.interval_s)
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

# ---------------------------
# GUI application (scaled ~50% smaller, with Completed tab)
# ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autonomous Prometheus Scanner (Scaled GUI)")
        self.geometry("800x520")      # ~50% smaller than original big layout
        self.minsize(650, 430)

        self.puzzle, self.scanner, self.missing, self.brain = demo_puzzle()
        self.monitor = SystemMonitor(interval_s=1.0)
        self.prober = ExternalProbe()
        self.monitor.start()

        # Autonomy managers
        self.external_auto = ExternalAutonomousScanner(self.prober, interval_s=5.0)
        self.missing_auto = MissingLinkAutonomy(self.puzzle, self.brain, interval_s=7.0)
        self.external_auto.start()
        self.missing_auto.start()

        self.dragging_node: Optional[str] = None
        self.node_positions: Dict[str, Tuple[int, int]] = {}
        self._init_layout()
        self._init_graph()
        self._log_autoload()
        self._refresh_all()
        self._start_gui_loop()

    def _init_layout(self):
        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # Left: Graph canvas
        left = ttk.Frame(main)
        main.add(left, weight=2)
        self.canvas = tk.Canvas(left, bg="#0f1115", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        ctrl = ttk.Frame(left); ctrl.pack(fill=tk.X)
        ttk.Label(ctrl, text="Node:").pack(side=tk.LEFT, padx=4)
        self.node_entry = ttk.Entry(ctrl, width=10); self.node_entry.pack(side=tk.LEFT)
        ttk.Button(ctrl, text="Add node", command=self._add_node).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="Scan", command=self._do_scan).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="Cave map", command=self._show_map_modal).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="Reset demo", command=self._reset_demo).pack(side=tk.RIGHT, padx=4)

        # Right: Tabs
        right = ttk.Notebook(main)
        main.add(right, weight=1)

        # System tab
        self.tab_sys = ttk.Frame(right); right.add(self.tab_sys, text="System")
        sys_top = ttk.Frame(self.tab_sys); sys_top.pack(fill=tk.X, padx=6, pady=6)
        self.cpu_label = ttk.Label(sys_top, text="CPU:"); self.cpu_label.pack(anchor="w")
        self.ram_label = ttk.Label(sys_top, text="RAM:"); self.ram_label.pack(anchor="w")
        self.disk_label = ttk.Label(sys_top, text="Disk:"); self.disk_label.pack(anchor="w")
        self.net_label = ttk.Label(sys_top, text="Net I/O:"); self.net_label.pack(anchor="w")
        self.gpu_label = ttk.Label(sys_top, text="GPU:"); self.gpu_label.pack(anchor="w")

        sys_mid = ttk.Frame(self.tab_sys); sys_mid.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.proc_tree = ttk.Treeview(sys_mid, columns=("pid","name","cpu","mem"), show="headings", height=8)
        for c, t in [("pid","PID"),("name","Name"),("cpu","CPU%"),("mem","Mem(MB)")]:
            self.proc_tree.heading(c, text=t)
        self.proc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        port_panel = ttk.Frame(sys_mid); port_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.port_counts_label = ttk.Label(port_panel, text="Ports:"); self.port_counts_label.pack(anchor="w")
        ttk.Label(port_panel, text="Listening Ports").pack(anchor="w", pady=(6,0))
        self.listening_tree = ttk.Treeview(port_panel, columns=("proto","local","pid","status"), show="headings", height=6)
        for c, t in [("proto","Proto"),("local","Local"),("pid","PID"),("status","Status")]:
            self.listening_tree.heading(c, text=t)
        self.listening_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        ttk.Label(port_panel, text="Active Connections").pack(anchor="w", pady=(6,0))
        self.conn_tree = ttk.Treeview(port_panel, columns=("proto","local","remote","pid","status"), show="headings", height=6)
        for c, t in [("proto","Proto"),("local","Local"),("remote","Remote"),("pid","PID"),("status","Status")]:
            self.conn_tree.heading(c, text=t)
        self.conn_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # External tab
        self.tab_ext = ttk.Frame(right); right.add(self.tab_ext, text="External")
        self.ext_output = tk.Text(self.tab_ext, height=16, wrap="word")
        self.ext_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        ext_scroll = ttk.Scrollbar(self.tab_ext, command=self.ext_output.yview)
        ext_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ext_output.config(yscrollcommand=ext_scroll.set)

        # Scan tab
        self.tab_scan = ttk.Frame(right); right.add(self.tab_scan, text="Scan")
        self.scan_output = tk.Text(self.tab_scan, height=16, wrap="word")
        self.scan_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        scan_scroll = ttk.Scrollbar(self.tab_scan, command=self.scan_output.yview)
        scan_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.scan_output.config(yscrollcommand=scan_scroll.set)

        # Completed tab (scrollable)
        self.tab_completed = ttk.Frame(right); right.add(self.tab_completed, text="Completed")
        completed_frame = ttk.Frame(self.tab_completed)
        completed_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.completed_text = tk.Text(completed_frame, height=16, wrap="word")
        self.completed_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        completed_scroll = ttk.Scrollbar(completed_frame, command=self.completed_text.yview)
        completed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.completed_text.config(yscrollcommand=completed_scroll.set)

        # Console tab
        self.tab_console = ttk.Frame(right); right.add(self.tab_console, text="Console")
        self.console = tk.Text(self.tab_console, height=16, wrap="word")
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        console_scroll = ttk.Scrollbar(self.tab_console, command=self.console.yview)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=console_scroll.set)

        # Canvas events
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_down)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_up)

    def _log_autoload(self):
        for line in AUTOLOAD_LOG:
            LOG_BUS.put(line)

    def _flush_logs(self):
        lines = LOG_BUS.get_all()
        if not lines:
            return
        for ln in lines:
            try:
                # Console
                self.console.insert(tk.END, ln + "\n")
                self.console.see(tk.END)
                # External mirror
                if "HTTP ping" in ln or "DNS lookup" in ln or "Port check" in ln:
                    self.ext_output.insert(tk.END, ln + "\n")
                    self.ext_output.see(tk.END)
                # Completed answers/results
                if ln.startswith("[Completed]") or ("Applied AI Brain proposal" in ln) or ("MissingLinkAutonomy applied" in ln):
                    self.completed_text.insert(tk.END, ln + "\n")
                    self.completed_text.see(tk.END)
            except Exception:
                pass

    def _init_graph(self):
        w = max(self.canvas.winfo_width(), 380)
        h = max(self.canvas.winfo_height(), 260)
        for pid in self.puzzle.pieces:
            self.node_positions[pid] = (random.randint(50, w-50), random.randint(50, h-50))

    def _draw_graph(self):
        self.canvas.delete("all")
        # edges
        for e in self.puzzle.edges:
            if e.a in self.node_positions and e.b in self.node_positions:
                ax, ay = self.node_positions[e.a]
                bx, by = self.node_positions[e.b]
                color = "#3aa1ff" if e.relation == "adjacent" else "#7f8c8d"
                self.canvas.create_line(ax, ay, bx, by, fill=color, width=2)
        # nodes
        for pid, pos in self.node_positions.items():
            x, y = pos
            attrs = self.puzzle.pieces[pid].attrs
            fill = "#1abc9c" if attrs else "#34495e"
            r = 12
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline="#ecf0f1", width=2, tags=f"node:{pid}")
            self.canvas.create_text(x, y, text=pid, fill="#ecf0f1", font=("Consolas", 9, "bold"))

    def _refresh_all(self):
        self._draw_graph()

    def _start_gui_loop(self):
        def tick():
            self._update_system_tab()
            self._flush_logs()
            self.after(1000, tick)
        self.after(1000, tick)

    # System tab updates
    def _update_system_tab(self):
        if not self.monitor.snapshots:
            return
        s = self.monitor.snapshots[-1]
        self.cpu_label.config(text=f"CPU: {s.cpu_percent:.1f}% | cores: {', '.join(f'{c:.0f}' for c in s.cpu_per_core)}")
        self.ram_label.config(text=f"RAM: {s.ram_used_mb:.0f}/{s.ram_total_mb:.0f} MB")
        self.disk_label.config(text=f"Disk: {s.disk_used_mb:.0f}/{s.disk_total_mb:.0f} MB")
        self.net_label.config(text=f"Net I/O: sent {s.net_bytes_sent/1e6:.2f} MB, recv {s.net_bytes_recv/1e6:.2f} MB")
        if s.gpu_info:
            g = s.gpu_info[0]
            self.gpu_label.config(text=f"GPU: {g['name']} load {g['load']}% mem {g['mem_used_mb']}/{g['mem_total_mb']} MB temp {g['temp_c']}°C")
        else:
            self.gpu_label.config(text="GPU: none or unavailable")
        # processes
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        for p in s.top_procs:
            self.proc_tree.insert("", tk.END, values=(p["pid"], p["name"], p["cpu"], p["mem_mb"]))
        # ports listening
        for i in self.listening_tree.get_children():
            self.listening_tree.delete(i)
        for li in s.ports_listening[:60]:
            proto = "TCP" if li["type"] == socket.SOCK_STREAM else ("UDP" if li["type"] == socket.SOCK_DGRAM else str(li["type"]))
            self.listening_tree.insert("", tk.END, values=(proto, li["laddr"], li["pid"], li["status"]))
        # active connections
        for i in self.conn_tree.get_children():
            self.conn_tree.delete(i)
        for co in s.connections[:100]:
            proto = "TCP" if co["type"] == socket.SOCK_STREAM else ("UDP" if co["type"] == socket.SOCK_DGRAM else str(co["type"]))
            self.conn_tree.insert("", tk.END, values=(proto, co["laddr"], co["raddr"], co["pid"], co["status"]))
        # counts
        self.port_counts_label.config(
            text=f"TCP LISTEN: {s.conn_counts['TCP_LISTEN']} | TCP ESTABLISHED: {s.conn_counts['TCP_ESTABLISHED']} | TCP OTHER: {s.conn_counts['TCP_OTHER']} | UDP: {s.conn_counts['UDP']}"
        )

    # Canvas interactivity
    def _node_at(self, event) -> Optional[str]:
        x, y = event.x, event.y
        for pid, (nx, ny) in self.node_positions.items():
            if (x - nx) ** 2 + (y - ny) ** 2 <= 12 ** 2:
                return pid
        return None

    def _on_canvas_down(self, event):
        pid = self._node_at(event)
        if pid:
            self.dragging_node = pid

    def _on_canvas_drag(self, event):
        if self.dragging_node:
            self.node_positions[self.dragging_node] = (event.x, event.y)
            self._draw_graph()

    def _on_canvas_up(self, event):
        if self.dragging_node:
            LOG_BUS.put(f"Moved node {self.dragging_node} to {self.node_positions[self.dragging_node]}")
            self.dragging_node = None

    # Puzzle controls
    def _add_node(self):
        pid = self.node_entry.get().strip()
        if not pid: return
        try:
            self.puzzle.add_piece(pid)
            self.node_positions[pid] = (random.randint(50, 380), random.randint(50, 260))
            LOG_BUS.put(f"Added node {pid}")
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _do_scan(self):
        self.scanner.scan()
        rep = self.scanner.report()
        self.scan_output.delete("1.0", tk.END)
        self.scan_output.insert(tk.END, rep["map"] + "\n\n")
        for layer in rep["layers"]:
            self.scan_output.insert(tk.END, f"-- {layer['name']} --\n")
            for n in layer["notes"]:
                self.scan_output.insert(tk.END, f"  {n}\n")
        LOG_BUS.put("[Completed] Scan completed and report generated.")

    def _show_map_modal(self):
        rep = self.scanner.report()
        win = tk.Toplevel(self)
        win.title("Cave Map")
        txt = tk.Text(win, width=80, height=24)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, rep["map"])
        LOG_BUS.put("Displayed cave map.")

    def _reset_demo(self):
        self.puzzle, self.scanner, self.missing, self.brain = demo_puzzle()
        LOG_BUS.put("[Completed] Demo puzzle reloaded to initial state.")
        self._init_graph()
        self._refresh_all()

# ---------------------------
# Entry point
# ---------------------------

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

