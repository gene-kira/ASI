"""
Fortune Teller — autonomous, network/web‑aware, and more predictive

What's new (USB removed, prediction upgraded):
- Telemetry focused on network/web:
  - Active window focus + process tree sampling
  - Network activity rates, connection counts, LAN scan (ARP + Zeroconf)
  - Mounted network shares (SMB/CIFS/NFS/UNC)
- Persona inference improved using ports/domains and LAN context
- Predictor upgrades:
  - Transformer‑lite attention over longer sequences
  - Time/persona‑conditioned models (autonomous)
  - Markov + k‑gram transitions with recency decay
  - Bandit learning and calibrated softmax with Platt-like correction
  - New: web/network signals (ports/domains) biasing
  - New: rolling trend bias (EWMA of per‑intent success over last N events)
  - New: co‑occurrence graph bias (learn pairs of intents that follow together)
- Planner upgrades:
  - Multi‑step chain widening up to 4 actions using transitions + co‑occurrence
- Policy:
  - Confidence‑weighted autonomy gating
- AutoLoader:
  - Capability‑aware prefetch scaling and adjustable read‑ahead

Note: USB detection and removable-drive scanning have been removed.
"""

# -------------------------------------------------------------------
# Imports and platform helpers
# -------------------------------------------------------------------

import os, sys, platform
import subprocess, threading, time, datetime, queue, json, hashlib, math, random, ipaddress
from collections import deque, Counter
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
import psutil

# Optional GPU probes
try:
    import pynvml; NVML_AVAILABLE = True
except Exception: NVML_AVAILABLE = False
try:
    import pyamdgpuinfo; AMD_AVAILABLE = True
except Exception: AMD_AVAILABLE = False

# Optional Windows active window
try:
    if platform.system() == "Windows":
        import win32gui, win32process  # requires pywin32
        WIN32_AVAILABLE = True
    else:
        WIN32_AVAILABLE = False
except Exception:
    WIN32_AVAILABLE = False

# Optional LAN discovery
try:
    from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange  # type: ignore
    ZEROCONF_AVAILABLE = True
except Exception: ZEROCONF_AVAILABLE = False
try:
    from scapy.all import ARP, Ether, srp  # type: ignore
    SCAPY_AVAILABLE = True
except Exception: SCAPY_AVAILABLE = False

# Optional input monitoring
try:
    from pynput import keyboard, mouse; PYNPUT_AVAILABLE = True
except Exception: PYNPUT_AVAILABLE = False

# Crypto
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except Exception: CRYPTO_AVAILABLE = False

# GUI detection
def _detect_headless() -> bool:
    if platform.system() in ("Linux", "Darwin"):
        if not os.environ.get("DISPLAY"): return True
    if platform.system() == "Windows":
        return not os.environ.get("SESSIONNAME") and not os.environ.get("USERNAME")
    return False
HEADLESS_MODE = _detect_headless()
try:
    if not HEADLESS_MODE:
        import tkinter as tk
        from tkinter import ttk
        TK_AVAILABLE = True
    else: TK_AVAILABLE = False
except Exception: TK_AVAILABLE = False

# -------------------------------------------------------------------
# Windows elevation — flag-aware, single attempt
# -------------------------------------------------------------------

def ensure_admin_once() -> bool:
    if platform.system() != "Windows":
        return True
    if "--elevated" in sys.argv:
        return True
    try:
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False
        if is_admin:
            return True
        script = os.path.abspath(sys.argv[0])
        args = [a for a in sys.argv[1:] if a != "--elevated"]
        params = " ".join([f'"{a}"' if " " in a else a for a in args] + ["--elevated"])
        rc = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        if rc <= 32:
            print(f"[Elevation] Relaunch failed (rc={rc}). Continuing without elevation.")
            return True
        return False  # parent exits, child runs elevated
    except Exception as e:
        print(f"[Elevation] Unexpected error: {e}. Continuing without elevation.")
        return True

# -------------------------------------------------------------------
# Borg Mesh configuration
# -------------------------------------------------------------------

BORG_MESH_CONFIG = {
    "max_corridors": 10_000,
    "unknown_bias": 0.35,
    "enforce_rate": 0.15,
}

# -------------------------------------------------------------------
# Dataclasses
# -------------------------------------------------------------------

@dataclass
class Intent:
    id: str
    score: float
    evidence: Dict[str, Any]
    deadline: Optional[datetime.datetime] = None
    cluster: Optional[str] = None
    calibrated: float = 0.0

@dataclass
class PlanStep:
    name: str
    deps: List[str] = field(default_factory=list)
    cost: Dict[str, float] = field(default_factory=dict)
    expected_gain_ms: int = 0

@dataclass
class Plan:
    id: str
    steps: List[PlanStep]
    total_cost: Dict[str, float]
    expected_gain_ms: int
    rationale: str
    chosen_intent: Optional[Intent] = None

@dataclass
class Decision:
    allow: bool
    notify: bool
    rationale: str
    risk: str
    policy_gate: Dict[str, Any]

@dataclass
class Result:
    success: bool
    resources: Dict[str, float]
    verified_hashes: Dict[str, str]
    notes: str

@dataclass
class CapabilityProfile:
    scores: Dict[str, float]
    features: Dict[str, bool]
    constraints: Dict[str, Any]

@dataclass
class Policy:
    autonomy_level: str
    cpu_cap: float
    disk_cap_bps: float
    vram_cap_mb: float
    quiet_hours: Tuple[int, int]
    privacy_scopes: Dict[str, Any]
    assist_not_act: bool = True
    suppress: List[str] = field(default_factory=list)
    promote: List[str] = field(default_factory=list)

@dataclass
class UpdatePolicy:
    allow_paths: List[str]
    max_patch_bytes: int
    quiet_hours: Tuple[int, int]
    require_tests_pass: bool
    require_lint_pass: bool
    create_backup: bool

@dataclass
class Patch:
    target_path: str
    description: str
    diff: str
    bytes: int

@dataclass
class UpdateResult:
    applied: bool
    rationale: str
    files_changed: List[str]
    backup_paths: List[str]
    signature: str
    version: Optional[str] = None

# ============================================================
# Borg dependencies — Comms, Guardian, privacy filter (stubs)
# ============================================================

class BorgCommsRouter:
    def __init__(self, logger): self.logger = logger
    def send_secure(self, topic: str, message: str, channel: str = "Default"):
        self.logger.log("borg_comms", f"{channel}:{topic}", {"msg": message[:500]})

class SecurityGuardian:
    def __init__(self, logger): self.logger = logger
    def disassemble(self, snippet: str) -> Dict[str, Any]:
        entropy = 0.0
        if snippet:
            counts = Counter(snippet); total = sum(counts.values())
            probs = [c/total for c in counts.values()] if total else [0.0]
            entropy = -sum(p*math.log(p+1e-12) for p in probs)
        flags = []
        if any(tag in snippet.lower() for tag in ["token","password","secret","ssn","bank"]):
            flags.append("PII_LIKE")
        if "http" in snippet.lower(): flags.append("LINKED")
        return {"entropy": entropy, "pattern_flags": flags}
    def _pii_count(self, snippet: str) -> int:
        terms = ["email@", "@", "ssn", "iban", "credit", "card", "password", "token"]
        s = snippet.lower(); return sum(1 for t in terms if t in s)
    def reassemble(self, url: str, cleaned_snippet: str, raw_pii_hits: int=0) -> Dict[str, Any]:
        status = "SAFE_FOR_TRAVEL" if raw_pii_hits==0 and len(cleaned_snippet)<2048 else "HOSTILE"
        self.logger.log("borg_guardian","Verdict",{"url":url,"status":status,"pii":raw_pii_hits})
        return {"url":url,"status":status,"pii":raw_pii_hits}

def privacy_filter(snippet: str) -> Tuple[str, Dict[str, Any]]:
    s = snippet or ""; redactions={}
    for token in ["token","password","secret","apikey","session"]:
        if token in s.lower():
            redactions[token]=True; s=s.replace(token,"[REDACTED]")
    return s, {"redactions": redactions}

# -------------------------------------------------------------------
# Crypto manager (per-machine AES-GCM)
# -------------------------------------------------------------------

class CryptoManager:
    def __init__(self, key_dir: str = ".ft_secrets"):
        self.available = CRYPTO_AVAILABLE
        self.key_dir = os.path.abspath(key_dir)
        self.salt_path = os.path.join(self.key_dir, "salt.bin")
        self.key_path = os.path.join(self.key_dir, "key.bin")
        self._aesgcm = None
        self._ensure_key()

    def _machine_fingerprint(self) -> bytes:
        fp = f"{platform.system()}|{platform.node()}|{platform.machine()}|{platform.processor()}"
        try:
            macs = []
            for _, addrs in psutil.net_if_addrs().items():
                for a in addrs:
                    addr = getattr(a, 'address', '')
                    if addr and addr.count(":") == 5:
                        macs.append(addr)
            if macs:
                fp += "|" + macs[0]
        except Exception:
            pass
        return hashlib.sha256(fp.encode("utf-8")).digest()

    def _ensure_key(self):
        if not self.available:
            return
        os.makedirs(self.key_dir, exist_ok=True)
        if not os.path.exists(self.salt_path):
            with open(self.salt_path, "wb") as f:
                f.write(os.urandom(16))
        with open(self.salt_path, "rb") as f:
            salt = f.read()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200000)
        derived = kdf.derive(self._machine_fingerprint())
        try:
            with open(self.key_path, "wb") as f:
                f.write(derived)
        except Exception:
            pass
        self._aesgcm = AESGCM(derived)

    def encrypt(self, data: bytes, aad: Optional[bytes] = None) -> bytes:
        if not self.available or not self._aesgcm:
            return data
        nonce = os.urandom(12)
        ct = self._aesgcm.encrypt(nonce, data, aad)
        return nonce + ct

    def decrypt(self, payload: bytes, aad: Optional[bytes] = None) -> bytes:
        if not self.available or not self._aesgcm:
            return payload
        nonce, ct = payload[:12], payload[12:]
        return self._aesgcm.decrypt(nonce, ct, aad)

    def seal_file(self, path: str, obj: Any):
        raw = json.dumps(obj, indent=2).encode("utf-8")
        enc = self.encrypt(raw, aad=b"fortune_teller")
        with open(path, "wb") as f:
            f.write(enc)

    def unseal_file(self, path: str) -> Any:
        with open(path, "rb") as f:
            payload = f.read()
        dec = self.decrypt(payload, aad=b"fortune_teller")
        return json.loads(dec.decode("utf-8"))

    def sign_text(self, text: str) -> str:
        fp = self._machine_fingerprint()
        return hashlib.sha256(text.encode("utf-8") + fp).hexdigest()

# -------------------------------------------------------------------
# Memory manager (encrypted + accuracy tracking + mesh events)
# -------------------------------------------------------------------

class MemoryManager:
    def __init__(self, crypto: CryptoManager, path: str = "fortune_teller_memory.enc"):
        self.crypto = crypto
        self.path = path
        self.state = {
            "weights": {},
            "transitions": {},
            "history": [],
            "accuracy": {"correct": 0, "total": 0},
            "per_intent": {},
            "suppression": [],
            "promotion": [],
            "mesh_log": []
        }
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                self.state = self.crypto.unseal_file(self.path)
            except Exception:
                legacy = self.path.replace(".enc", ".json")
                if os.path.exists(legacy):
                    try:
                        with open(legacy, "r", encoding="utf-8") as f:
                            self.state = json.load(f)
                    except Exception:
                        pass
        for k, v in [
            ("accuracy", {"correct": 0, "total": 0}),
            ("per_intent", {}),
            ("history", []),
            ("weights", {}),
            ("transitions", {}),
            ("suppression", []),
            ("promotion", []),
            ("mesh_log", []),
        ]:
            if k not in self.state or not isinstance(self.state[k], type(v)):
                self.state[k] = v

    def save(self):
        try:
            self.crypto.seal_file(self.path, self.state)
        except Exception:
            pass

    def record_outcome(self, action: str, success: bool, context: Dict[str, Any]):
        self.state["history"].append({
            "ts": datetime.datetime.utcnow().isoformat(),
            "action": action,
            "success": success,
            "context": context,
        })
        acc = self.state.setdefault("accuracy", {"correct": 0, "total": 0})
        acc["total"] += 1
        if success:
            acc["correct"] += 1

        pi = self.state.setdefault("per_intent", {})
        st = pi.setdefault(action, {"correct": 0, "total": 0})
        st["total"] += 1
        if success:
            st["correct"] += 1

        if len(self.state["history"]) > 4000:
            self.state["history"] = self.state["history"][-4000:]

    def set_weights(self, weights: Dict[str, float]):
        self.state["weights"] = weights

    def get_weights(self) -> Dict[str, float]:
        return dict(self.state.get("weights", {}))

    def set_transitions(self, transitions: Dict[str, int]):
        self.state["transitions"] = transitions

    def get_transitions(self) -> Dict[str, int]:
        return dict(self.state.get("transitions", {}))

    def get_accuracy(self) -> Dict[str, int]:
        acc = self.state.get("accuracy")
        if not acc or not isinstance(acc, dict):
            acc = {"correct": 0, "total": 0}
            self.state["accuracy"] = acc
        return dict(acc)

    def set_feedback(self, suppress: List[str], promote: List[str]):
        self.state["suppression"] = suppress
        self.state["promotion"] = promote

    def get_feedback(self) -> Tuple[List[str], List[str]]:
        return (list(self.state.get("suppression", [])), list(self.state.get("promotion", [])))

    def record_mesh_event(self, evt: Dict[str, Any]):
        mesh_log = self.state.setdefault("mesh_log", [])
        mesh_log.append(evt)
        if len(mesh_log) > 5000:
            self.state["mesh_log"] = mesh_log[-5000:]
        self.save()

# -------------------------------------------------------------------
# Logger (encrypted flush)
# -------------------------------------------------------------------

class Logger:
    def __init__(self, crypto: CryptoManager, enc_path: str = "fortune_teller_logs.enc"):
        self.events = queue.Queue()
        self.counters: Dict[str, int] = {}
        self.crypto = crypto
        self.enc_path = enc_path
        self._last_flush = time.time()

    def log(self, kind: str, message: str, meta: Optional[Dict[str, Any]] = None):
        entry = {
            "ts": datetime.datetime.utcnow().isoformat(),
            "kind": kind,
            "message": message,
            "meta": meta or {}
        }
        self.events.put(entry)
        self.counters[kind] = self.counters.get(kind, 0) + 1

    def drain(self, max_items=200) -> List[Dict[str, Any]]:
        out = []
        while not self.events.empty() and len(out) < max_items:
            out.append(self.events.get())
        now = time.time()
        if (now - self._last_flush) > 5 and out:
            self._flush_persist(out)
            self._last_flush = now
        return out

    def count(self, kind: str) -> int:
        return self.counters.get(kind, 0)

    def _flush_persist(self, entries: List[Dict[str, Any]]):
        try:
            payload = {"entries": entries, "sig": self.crypto.sign_text(json.dumps(entries))}
            raw = json.dumps(payload).encode("utf-8")
            enc = self.crypto.encrypt(raw, aad=b"fortune_teller_logs")
            with open(self.enc_path, "ab") as f:
                f.write(enc + b"\n")
        except Exception:
            pass

# -------------------------------------------------------------------
# Input activity monitor (mouse + keyboard)
# -------------------------------------------------------------------

class InputMonitor:
    def __init__(self, logger: Logger, window_sec: float = 1.0):
        self.logger = logger
        self.window_sec = window_sec
        self.stop_flag = False
        self.stats_lock = threading.Lock()
        self._mouse_listener = None
        self._keyboard_listener = None
        self.mouse_moves = 0
        self.mouse_clicks = 0
        self.mouse_scrolls = 0
        self.keypresses = 0

    def _reset_stats(self):
        self.mouse_moves = 0
        self.mouse_clicks = 0
        self.mouse_scrolls = 0
        self.keypresses = 0

    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()
        if PYNPUT_AVAILABLE:
            try:
                self._mouse_listener = mouse.Listener(on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll)
                self._mouse_listener.start()
                self._keyboard_listener = keyboard.Listener(on_press=self._on_press)
                self._keyboard_listener.start()
                self.logger.log("input", "InputMonitor started with pynput")
            except Exception as e:
                self.logger.log("input", "InputMonitor failed to start pynput", {"error": str(e)})
        else:
            self.logger.log("input", "InputMonitor running in fallback mode")

    def _on_move(self, x, y):
        with self.stats_lock:
            self.mouse_moves += 1

    def _on_click(self, x, y, button, pressed):
        if pressed:
            with self.stats_lock:
                self.mouse_clicks += 1

    def _on_scroll(self, x, y, dx, dy):
        with self.stats_lock:
            self.mouse_scrolls += 1

    def _on_press(self, key):
        with self.stats_lock:
            self.keypresses += 1

    def snapshot(self) -> Dict[str, Any]:
        with self.stats_lock:
            mm, mc, ms, kp = self.mouse_moves, self.mouse_clicks, self.mouse_scrolls, self.keypresses
            cadence_mouse = min(1.0, (mm + mc + ms) / 100.0)
            cadence_keyboard = min(1.0, kp / 80.0)
            active = (mm + mc + ms + kp) > 0
            self._reset_stats()
        return {
            "mouse_moves": mm,
            "mouse_clicks": mc,
            "mouse_scrolls": ms,
            "keypresses": kp,
            "cadence_mouse": cadence_mouse,
            "cadence_keyboard": cadence_keyboard,
            "active": active
        }

    def _loop(self):
        while not self.stop_flag:
            snap = self.snapshot()
            self.logger.log("input_tick", "Input cadence", {"cadence": snap})
            time.sleep(self.window_sec)

    def stop(self):
        self.stop_flag = True
        try:
            if self._mouse_listener: self._mouse_listener.stop()
            if self._keyboard_listener: self._keyboard_listener.stop()
        except Exception:
            pass
        self.logger.log("input", "InputMonitor stopped")

# -------------------------------------------------------------------
# Drive and network activity analyzer
# -------------------------------------------------------------------

class ActivityAnalyzer:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.prev_disk = None
        self.prev_net = None
        self.last_ts = None

    def snapshot(self) -> Dict[str, Any]:
        now = time.time()
        disk_counters = psutil.disk_io_counters(perdisk=True)
        net_counters = psutil.net_io_counters()

        rates = {
            "drives": {},
            "net": {"up_bps": 0.0, "down_bps": 0.0, "connections": 0, "status": "idle", "ports_hint": []}
        }

        if self.prev_disk is not None and self.last_ts is not None:
            dt = max(0.001, now - self.last_ts)
            for name, cnt in disk_counters.items():
                prev = self.prev_disk.get(name) if isinstance(self.prev_disk, dict) else None
                if prev:
                    r_bps = max(0.0, (cnt.read_bytes - prev.read_bytes) / dt)
                    w_bps = max(0.0, (cnt.write_bytes - prev.write_bytes) / dt)
                    busy = getattr(cnt, "busy_time", 0.0)
                    rates["drives"][name] = {"read_bps": r_bps, "write_bps": w_bps, "busy_time_ms": busy}
        self.prev_disk = disk_counters

        if self.prev_net is not None and self.last_ts is not None and net_counters is not None:
            dt = max(0.001, now - self.last_ts)
            up_bps = max(0.0, (net_counters.bytes_sent - self.prev_net.bytes_sent) / dt)
            down_bps = max(0.0, (net_counters.bytes_recv - self.prev_net.bytes_recv) / dt)
            rates["net"]["up_bps"] = up_bps
            rates["net"]["down_bps"] = down_bps

        self.prev_net = net_counters
        self.last_ts = now

        conns = []
        try:
            conns = [c for c in psutil.net_connections(kind='inet') if c.status == "ESTABLISHED"]
        except Exception:
            conns = []
        rates["net"]["connections"] = len(conns)

        # Ports hint to help persona inference and predictor
        ports = Counter()
        for c in conns[:100]:
            try:
                if c.laddr and c.raddr:
                    ports[c.raddr.port] += 1
            except Exception:
                pass
        common_ports = [p for p, _ in ports.most_common(8)]
        rates["net"]["ports_hint"] = common_ports

        status = "idle"
        up = rates["net"]["up_bps"]
        down = rates["net"]["down_bps"]
        total_drive_rw = sum((d["read_bps"] + d["write_bps"]) for d in rates["drives"].values()) if rates["drives"] else 0.0
        if down > 500_000 and rates["net"]["connections"] > 5 and total_drive_rw < 20_000_000:
            status = "browsing"
        if (up > 300_000 and down > 300_000) and rates["net"]["connections"] > 20 and total_drive_rw < 15_000_000:
            status = "gaming"
        if (up > 5_000_000 or down > 10_000_000) or total_drive_rw > 50_000_000:
            status = "transfer"
        rates["net"]["status"] = status

        self.logger.log("activity", "Drive/Net activity", {"rates": rates})
        return rates

# -------------------------------------------------------------------
# Telemetry collector (network shares + LAN scan + web-aware inference)
# -------------------------------------------------------------------

class TelemetryCollector:
    def __init__(self, logger: Logger, input_monitor: InputMonitor, activity: ActivityAnalyzer):
        self.logger = logger
        self.input_monitor = input_monitor
        self.activity = activity
        self.stop_flag = False

    def start(self):
        self.input_monitor.start()
        threading.Thread(target=self._loop, daemon=True).start()
        self.logger.log("telemetry", "Telemetry started")

    def _gpu_snapshot(self) -> Dict[str, Any]:
        gpu = {"vendor": None, "util": 0.0, "vram_total_mb": 0.0, "vram_free_mb": 0.0}
        try:
            if NVML_AVAILABLE:
                try:
                    pynvml.nvmlInit()
                    h = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
                    mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                    gpu.update({
                        "vendor": "NVIDIA",
                        "util": float(util),
                        "vram_total_mb": mem.total / (1024 * 1024),
                        "vram_free_mb": mem.free / (1024 * 1024)
                    })
                finally:
                    try: pynvml.nvmlShutdown()
                    except Exception: pass
            elif AMD_AVAILABLE:
                try:
                    devs = pyamdgpuinfo.get_gpu_info()
                    if devs:
                        dev = devs[0]
                        gpu.update({
                            "vendor": "AMD",
                            "util": 0.0,
                            "vram_total_mb": float(dev.get("vram_total", 0.0)),
                            "vram_free_mb": 0.0
                        })
                except Exception:
                    pass
        except Exception as e:
            self.logger.log("telemetry", "GPU probe failed; CPU-only mode", {"error": str(e)})
            gpu = {"vendor": None, "util": 0.0, "vram_total_mb": 0.0, "vram_free_mb": 0.0}
        if gpu["vendor"] is None:
            self.logger.log("telemetry", "No GPU detected, running CPU-only mode")
        return gpu

    def _active_window(self) -> Dict[str, Any]:
        info = {"title": None, "exe": None, "pid": None}
        try:
            if WIN32_AVAILABLE:
                hwnd = win32gui.GetForegroundWindow()
                pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                title = win32gui.GetWindowText(hwnd)
                exe = None
                for p in psutil.process_iter(["pid", "name"]):
                    if p.info["pid"] == pid:
                        exe = p.info["name"]
                        break
                info.update({"title": title, "exe": exe, "pid": pid})
        except Exception:
            pass
        return info

    def _process_tree_sample(self, max_nodes: int = 50) -> List[Dict[str, Any]]:
        out = []
        try:
            for p in psutil.process_iter(["pid","ppid","name","username"]):
                out.append(p.info)
                if len(out) >= max_nodes:
                    break
        except Exception:
            pass
        return out

    def _network_shares_snapshot(self, max_items: int = 20) -> List[Dict[str, Any]]:
        shares: List[Dict[str, Any]] = []
        try:
            for part in psutil.disk_partitions(all=True):
                fs = (part.fstype or "").lower()
                mp = part.mountpoint
                dev = part.device
                is_network = False
                # Windows UNC path
                if platform.system() == "Windows" and dev.startswith("\\\\"):
                    is_network = True
                # Common network fs types
                if fs in ("cifs", "smbfs", "nfs", "nfs4", "afp", "glusterfs"):
                    is_network = True
                if is_network:
                    shares.append({"device": dev, "mountpoint": mp, "fstype": fs})
                    if len(shares) >= max_items:
                        break
        except Exception as e:
            self.logger.log("telemetry", "Network shares snapshot failed", {"error": str(e)})
        return shares

    def _lan_cidr_guess(self) -> Optional[str]:
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for a in addrs:
                    if getattr(a, "family", None) == getattr(psutil, "AF_INET", None) or getattr(a, "family", None) == 2:
                        ip = getattr(a, "address", None)
                        netmask = getattr(a, "netmask", None)
                        if ip and netmask and not ip.startswith("127.") and ":" not in ip:
                            try:
                                net = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                                return str(net)
                            except Exception:
                                pass
        except Exception:
            pass
        return None

    def _lan_scan(self, timeout: float = 1.5, max_hosts: int = 32) -> Dict[str, Any]:
        result = {"arp_hosts": [], "zeroconf_services": []}
        # ARP scan
        try:
            cidr = self._lan_cidr_guess()
            if SCAPY_AVAILABLE and cidr:
                net = ipaddress.ip_network(cidr, strict=False)
                targets = []
                for i, ip in enumerate(net.hosts()):
                    targets.append(str(ip))
                    if len(targets) >= max_hosts:
                        break
                pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=" ".join(targets))  # type: ignore
                ans, _ = srp(pkt, timeout=timeout, verbose=False)  # type: ignore
                for _, rcv in ans:
                    ip = rcv.psrc
                    mac = rcv.hwsrc
                    result["arp_hosts"].append({"ip": ip, "mac": mac})
        except Exception as e:
            self.logger.log("telemetry", "LAN ARP scan failed", {"error": str(e)})

        # Zeroconf browse (short)
        try:
            if ZEROCONF_AVAILABLE:
                class _Listener:
                    def __init__(self): self.services = []
                    def add_service(self, zc, t, name):
                        self.services.append({"type": t, "name": name})
                    def remove_service(self, zc, t, name): pass
                    def update_service(self, zc, t, name): pass
                zc = Zeroconf()
                listener = _Listener()
                types = ["_http._tcp.local.", "_workstation._tcp.local."]
                browsers = [ServiceBrowser(zc, t, listener) for t in types]
                time.sleep(1.0)
                result["zeroconf_services"] = listener.services[:10]
                zc.close()
        except Exception as e:
            self.logger.log("telemetry", "Zeroconf browse failed", {"error": str(e)})

        return result

    def _web_context_hint(self, ports_hint: List[int]) -> Dict[str, float]:
        # Heuristics translating port presence into context hints
        hints = {"gaming": 0.0, "browsing": 0.0, "work": 0.0, "transfer": 0.0}
        for p in ports_hint:
            if p in (80, 443): hints["browsing"] += 0.2
            if p in (27015, 27036, 27037): hints["gaming"] += 0.25  # Steam/game servers
            if p in (22, 5432, 3306): hints["work"] += 0.2        # dev ops/db work
            if p in (445, 139, 2049): hints["transfer"] += 0.2    # SMB/NFS
        # Normalize
        total = sum(hints.values()) or 1.0
        for k in hints:
            hints[k] = min(1.0, hints[k] / total)
        return hints

    def snapshot(self) -> Dict[str, Any]:
        cpu_util = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        battery = None
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                battery = {"percent": batt.percent, "plugged": batt.power_plugged}
        except Exception:
            battery = None

        gpu = self._gpu_snapshot()
        now = datetime.datetime.now()
        input_state = self.input_monitor.snapshot()
        activity = self.activity.snapshot()
        active_win = self._active_window()
        proc_tree = self._process_tree_sample()
        net_shares = self._network_shares_snapshot()
        lan_info = self._lan_scan()

        persona = "Idle"
        status = activity.get("net", {}).get("status", "idle")
        kb = input_state.get("cadence_keyboard", 0.0)
        ms = input_state.get("cadence_mouse", 0.0)
        ports_hint = activity.get("net", {}).get("ports_hint", [])
        web_hint = self._web_context_hint(ports_hint)

        procs = []
        try:
            for p in psutil.process_iter(["name"]):
                n = (p.info.get("name") or "").lower()
                if n:
                    procs.append(n)
        except Exception:
            pass

        gaming_proc = any(n in procs for n in ["steam.exe", "epicgameslauncher.exe"])
        ide_proc = any(n in procs for n in ["code.exe", "idea64.exe", "pycharm64.exe", "devenv.exe"])
        browser_proc = any(n in procs for n in ["chrome.exe", "msedge.exe", "firefox.exe"])

        # Persona inference combining process signals, activity, and web hints
        if gaming_proc or status == "gaming" or web_hint.get("gaming", 0.0) > 0.4:
            persona = "Gaming"
        elif ide_proc or (kb > 0.5 and status in ("transfer", "idle")) or web_hint.get("work", 0.0) > 0.4:
            persona = "Work"
        elif browser_proc or status == "browsing" or ms > 0.6 or web_hint.get("browsing", 0.0) > 0.4:
            persona = "Browsing"

        return {
            "ts": now.isoformat(),
            "os": platform.system(),
            "cpu_util": cpu_util,
            "mem_total_mb": mem.total / (1024 * 1024),
            "mem_free_mb": mem.available / (1024 * 1024),
            "disk_io": disk_io._asdict() if disk_io else {},
            "net_io": net_io._asdict() if net_io else {},
            "gpu": gpu,
            "battery": battery,
            "hour": now.hour,
            "weekday": now.weekday(),
            "input_state": input_state,
            "activity": activity,
            "persona": persona,
            "proc_sample": procs[:25],
            "active_window": active_win,
            "proc_tree_sample": proc_tree,
            "network_shares": net_shares,
            "lan_scan": lan_info,
            "web_hint": web_hint,
            "headless": HEADLESS_MODE
        }

    def _loop(self):
        while not self.stop_flag:
            time.sleep(1.0)

    def stop(self):
        self.stop_flag = True
        self.logger.log("telemetry", "Telemetry stopped")

# -------------------------------------------------------------------
# Hardened Capability Profiler
# -------------------------------------------------------------------

class CapabilityProfiler:
    def __init__(self, logger: Logger, telemetry: TelemetryCollector):
        self.logger = logger
        self.telemetry = telemetry
        self.profile = CapabilityProfile(
            scores={"cpu": 0.6, "gpu": 0.5, "mem": 0.6, "disk": 0.7, "net": 0.6, "power": 0.6},
            features={"avx2": False, "directstorage": False, "tls_tickets": True},
            constraints={"battery": False, "numa_nodes": 1, "vm": False}
        )

    def _safe_num(self, val: Any, default: float = 0.0) -> float:
        try:
            if val is None: return default
            return float(val)
        except Exception:
            return default

    def _detect_avx2(self) -> bool:
        try:
            import platform as _plat, subprocess as _sub
            sysname = _plat.system()
            if sysname == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        cpuinfo = f.read().lower()
                    return "avx2" in cpuinfo
                except Exception:
                    return "x86_64" in _plat.machine()
            elif sysname == "Windows":
                return "AMD64" in _plat.machine() or "x86_64" in _plat.machine()
            elif sysname == "Darwin":
                try:
                    r = _sub.run(["sysctl", "machdep.cpu.features"], capture_output=True, text=True, timeout=2)
                    return "avx2" in (r.stdout or "").lower()
                except Exception:
                    return "x86_64" in _plat.machine()
            return "x86_64" in _plat.machine()
        except Exception:
            return False

    def _is_probably_vm(self) -> bool:
        try:
            import platform as _plat
            node = (_plat.node() or "").lower()
            machine = (_plat.machine() or "").lower()
            hints = ["virtual", "vm", "hyper", "kvm", "qemu", "vbox", "parallels"]
            return any(h in node for h in hints) or any(h in machine for h in hints)
        except Exception:
            return False

    def run_probes(self):
        try:
            snap = self.telemetry.snapshot()
        except Exception as e:
            self.logger.log("capability_error", "Telemetry snapshot failed", {"error": str(e)})
            return

        cpu_util = self._safe_num(snap.get("cpu_util"), 50.0)
        mem_total_mb = self._safe_num(snap.get("mem_total_mb"), 1024.0)
        mem_free_mb = self._safe_num(snap.get("mem_free_mb"), 512.0)
        battery = snap.get("battery") or {}
        plugged = bool(battery.get("plugged", False))

        gpu = snap.get("gpu") or {}
        gpu_vendor = gpu.get("vendor")
        gpu_score = 0.7 if gpu_vendor else 0.5

        cpu_score = min(1.0, max(0.0, (1.0 - cpu_util / 100.0) * 0.5 + 0.5))
        mem_score = min(1.0, max(0.0, mem_free_mb / max(256.0, mem_total_mb)))
        disk_score = 0.7
        net_score = 0.6
        power_score = 0.7 if plugged or battery == {} else 0.5

        self.profile.scores.update({
            "cpu": cpu_score,
            "gpu": gpu_score,
            "mem": mem_score,
            "disk": disk_score,
            "net": net_score,
            "power": power_score
        })
        self.profile.features["avx2"] = self._detect_avx2()
        self.profile.features["directstorage"] = (platform.system() == "Windows")
        self.profile.constraints["battery"] = bool(battery) and not plugged
        self.profile.constraints["vm"] = self._is_probably_vm()

        self.logger.log("capability", "Capability profile updated", {
            "scores": self.profile.scores,
            "features": self.profile.features,
            "constraints": self.profile.constraints
        })

    def get_profile(self) -> CapabilityProfile:
        return self.profile

# -------------------------------------------------------------------
# Borg mesh — network within the network (overlay)
# -------------------------------------------------------------------

class BorgMesh:
    def __init__(self, memory: MemoryManager, comms: BorgCommsRouter, guardian: SecurityGuardian):
        self.nodes = {}
        self.edges = set()
        self.memory = memory
        self.comms = comms
        self.guardian = guardian
        self.max_corridors = BORG_MESH_CONFIG["max_corridors"]

    def _risk(self, snippet: str) -> int:
        dis = self.guardian.disassemble(snippet or "")
        base = int(dis["entropy"] * 12) + len(dis["pattern_flags"]) * 10
        return max(0, min(100, base))

    def discover(self, url: str, snippet: str, links: List[str]):
        risk = self._risk(snippet)
        node = self.nodes.get(url, {"state": "discovered", "risk": risk, "seen": 0})
        node["state"] = "discovered"; node["risk"] = risk; node["seen"] += 1
        self.nodes[url] = node
        for l in links[:20]:
            if len(self.edges) < self.max_corridors:
                self.edges.add((url, l))
        evt = {"time": datetime.datetime.now().isoformat(timespec="seconds"),
               "type": "discover", "url": url, "risk": risk, "links": len(links)}
        self.memory.record_mesh_event(evt)
        self.comms.send_secure("mesh:discover", f"{url} risk={risk} links={len(links)}", "Default")

    def build(self, url: str) -> bool:
        if url not in self.nodes:
            return False
        self.nodes[url]["state"] = "built"
        evt = {"time": datetime.datetime.now().isoformat(timespec="seconds"),
               "type": "build", "url": url}
        self.memory.record_mesh_event(evt)
        self.comms.send_secure("mesh:build", f"{url} built", "Default")
        return True

    def enforce(self, url: str, snippet: str) -> bool:
        if url not in self.nodes:
            return False
        cleaned, _meta = privacy_filter(snippet or "")
        verdict = self.guardian.reassemble(url, cleaned, raw_pii_hits=self.guardian._pii_count(snippet or ""))
        status = verdict.get("status", "HOSTILE")
        self.nodes[url]["state"] = "enforced"
        self.nodes[url]["risk"] = 0 if status == "SAFE_FOR_TRAVEL" else max(50, self.nodes[url]["risk"])
        evt = {"time": datetime.datetime.now().isoformat(timespec="seconds"),
               "type": "enforce", "url": url, "status": status}
        self.memory.record_mesh_event(evt)
        self.comms.send_secure("mesh:enforce", f"{url} status={status}", "Default")
        return True

    def stats(self) -> Dict[str, Any]:
        total = len(self.nodes)
        discovered = sum(1 for n in self.nodes.values() if n["state"] == "discovered")
        built = sum(1 for n in self.nodes.values() if n["state"] == "built")
        enforced = sum(1 for n in self.nodes.values() if n["state"] == "enforced")
        return {"total": total, "discovered": discovered, "built": built,
                "enforced": enforced, "corridors": len(self.edges)}

# -------------------------------------------------------------------
# Borg roles — scanners, workers, enforcers
# -------------------------------------------------------------------

@dataclass
class MeshEvent:
    url: str
    snippet: str
    links: List[str]

class BorgScanner(threading.Thread):
    def __init__(self, mesh: BorgMesh, in_events: queue.Queue, out_ops: queue.Queue, label="SCANNER"):
        super().__init__(daemon=True)
        self.mesh = mesh; self.in_events = in_events; self.out_ops = out_ops
        self.label = label; self.running = True
    def stop(self): self.running = False
    def run(self):
        while self.running:
            try: ev: MeshEvent = self.in_events.get(timeout=1.0)
            except queue.Empty: continue
            unseen_links = [l for l in ev.links if l not in self.mesh.nodes and random.random() < BORG_MESH_CONFIG["unknown_bias"]]
            self.mesh.discover(ev.url, ev.snippet, unseen_links or ev.links)
            self.out_ops.put(("build", ev.url))
            time.sleep(random.uniform(0.2, 0.6))

class BorgWorker(threading.Thread):
    def __init__(self, mesh: BorgMesh, ops_q: queue.Queue, label="WORKER"):
        super().__init__(daemon=True)
        self.mesh = mesh; self.ops_q = ops_q; self.label = label; self.running = True
    def stop(self): self.running = False
    def run(self):
        while self.running:
            try: op, url = self.ops_q.get(timeout=1.0)
            except queue.Empty: continue
            if op == "build":
                if self.mesh.build(url): self.ops_q.put(("enforce", url))
            elif op == "enforce":
                self.mesh.enforce(url, snippet="")
            time.sleep(random.uniform(0.2, 0.5))

class BorgEnforcer(threading.Thread):
    def __init__(self, mesh: BorgMesh, guardian: SecurityGuardian, label="ENFORCER"):
        super().__init__(daemon=True)
        self.mesh = mesh; self.guardian = guardian; self.label = label; self.running = True
    def stop(self): self.running = False
    def run(self):
        while self.running:
            for url, meta in list(self.mesh.nodes.items()):
                if meta["state"] in ("built", "enforced") and random.random() < BORG_MESH_CONFIG["enforce_rate"]:
                    self.mesh.enforce(url, snippet="")
            time.sleep(1.2)

# -------------------------------------------------------------------
# Anomaly detector
# -------------------------------------------------------------------

class AnomalyDetector:
    def __init__(self, logger: Logger, window: int = 60):
        self.logger = logger
        self.window = window
        self.buffer: deque = deque(maxlen=window)
        self.thresholds = {
            "kb_cadence_z": 2.0,
            "mouse_cadence_z": 2.0,
            "net_bps_z": 2.5,
            "persona_switch_rate": 0.35,
        }
        self.persona_history: deque = deque(maxlen=window)

    def _z(self, series: List[float], x: float) -> float:
        if len(series) < 8:
            return 0.0
        mu = sum(series) / len(series)
        var = sum((s - mu) ** 2 for s in series) / len(series)
        sigma = max(1e-6, var ** 0.5)
        return (x - mu) / sigma

    def observe(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        inp = snapshot.get("input_state", {})
        activity = snapshot.get("activity", {})
        persona = snapshot.get("persona", "Idle")

        kb = float(inp.get("cadence_keyboard", 0.0))
        ms = float(inp.get("cadence_mouse", 0.0))
        net_up = float(activity.get("net", {}).get("up_bps", 0.0))
        net_down = float(activity.get("net", {}).get("down_bps", 0.0))
        net_total = net_up + net_down

        self.buffer.append({"kb": kb, "ms": ms, "net": net_total})
        self.persona_history.append(persona)

        kb_series = [b["kb"] for b in self.buffer]
        ms_series = [b["ms"] for b in self.buffer]
        net_series = [b["net"] for b in self.buffer]

        kb_z = self._z(kb_series, kb)
        ms_z = self._z(ms_series, ms)
        net_z = self._z(net_series, net_total)

        switches = 0
        ph = list(self.persona_history)
        for i in range(1, len(ph)):
            if ph[i] != ph[i - 1]:
                switches += 1
        switch_rate = (switches / max(1, len(ph))) if ph else 0.0

        anomalies = {
            "kb_z": kb_z > self.thresholds["kb_cadence_z"],
            "ms_z": ms_z > self.thresholds["mouse_cadence_z"],
            "net_z": net_z > self.thresholds["net_bps_z"],
            "persona_switch": switch_rate > self.thresholds["persona_switch_rate"],
        }
        active = any(anomalies.values())
        if active:
            self.logger.log("anomaly", "Anomaly detected", {"kb_z": kb_z, "ms_z": ms_z, "net_z": net_z, "switch_rate": switch_rate})
        return {"active": active, "anomalies": anomalies, "kb_z": kb_z, "ms_z": ms_z, "net_z": net_z, "switch_rate": switch_rate}

# -------------------------------------------------------------------
# Predictor (ensemble + personas + k-gram + bandit + calibration + attention + web-aware bias + trends)
# -------------------------------------------------------------------

class Predictor:
    def __init__(self, logger: Logger, memory: MemoryManager, policy: Policy):
        self.logger = logger
        self.memory = memory
        self.policy = policy
        self.action_weights: Dict[str, float] = self.memory.get_weights() or {
            "Open Email": 0.6,
            "Launch Browser": 0.7,
            "Launch Steam": 0.5,
            "Open IDE": 0.4,
        }
        self.transitions: Dict[str, int] = self.memory.get_transitions()
        self.last_action: Optional[str] = None
        self.last_action_ts: Optional[float] = None

        self.hour_hist: Dict[int, Dict[str, float]] = {h: {} for h in range(24)}
        self.weekday_hist: Dict[int, Dict[str, float]] = {d: {} for d in range(7)}
        self.ema_alpha = 0.2

        self.k_max = 5
        self.recency_decay = 0.965
        self.history = deque(maxlen=48)
        self.kgram_transitions: Dict[int, Dict[str, int]] = {k: {} for k in range(2, self.k_max + 1)}

        self.bandit_alpha: Dict[str, float] = {k: 1.0 for k in self.action_weights}
        self.bandit_beta: Dict[str, float] = {k: 1.0 for k in self.action_weights}

        self.platt_A = 1.0
        self.platt_B = 0.0

        self.cooldown: Dict[str, float] = {k: 0.0 for k in self.action_weights}
        self.rhythm: Dict[str, Tuple[int, int]] = {
            "Open Email": (7, 12),
            "Open IDE": (9, 18),
            "Launch Steam": (18, 23),
            "Launch Browser": (8, 23),
        }

        self.novelty: Dict[str, float] = {k: 0.0 for k in self.action_weights.keys()}
        self.clusters: Dict[str, str] = {
            "Open Email": "Productivity",
            "Open IDE": "Productivity",
            "Launch Browser": "Browsing",
            "Launch Steam": "Gaming",
        }

        # Persona-conditioned models (autonomous)
        self.persona_models = {
            "Work": {"hour_hist": {h:{} for h in range(24)}, "weekday_hist": {d:{} for d in range(7)}},
            "Gaming": {"hour_hist": {h:{} for h in range(24)}, "weekday_hist": {d:{} for d in range(7)}},
            "Browsing": {"hour_hist": {h:{} for h in range(24)}, "weekday_hist": {d:{} for d in range(7)}},
            "Idle": {"hour_hist": {h:{} for h in range(24)}, "weekday_hist": {d:{} for d in range(7)}},
        }
        self.blend_lambda = 0.6

        # Transformer-lite attention over recent actions
        self.attn_window = 16
        self.attn_keys = {a: random.random() for a in self.action_weights}
        self.attn_strength = 0.12

        # Rolling trend bias (EWMA per intent)
        self.trend: Dict[str, float] = {k: 0.5 for k in self.action_weights}
        self.trend_alpha = 0.15

        # Co-occurrence graph: boost pairs that often happen together
        self.cooccur: Dict[Tuple[str, str], int] = {}

    def _pm(self, persona: str):
        return self.persona_models.get(persona, self.persona_models["Idle"])

    def _ema_update(self, hist: Dict[str, float], key: str, inc: float = 1.0):
        val = hist.get(key, 0.0)
        hist[key] = (1 - self.ema_alpha) * val + self.ema_alpha * inc

    def _kgram_key(self, seq: List[str], next_action: Optional[str] = None) -> str:
        parts = list(seq)
        if next_action is not None:
            parts.append(next_action)
        return "||".join(parts)

    def _update_kgrams(self, action: str, success: bool):
        for k in self.kgram_transitions:
            for key in list(self.kgram_transitions[k].keys()):
                self.kgram_transitions[k][key] = int(self.kgram_transitions[k][key] * self.recency_decay)
        self.history.append(action)
        seq = list(self.history)
        for k in range(2, self.k_max + 1):
            if len(seq) >= k:
                window = seq[-k:]
                key = self._kgram_key(window)
                self.kgram_transitions[k][key] = self.kgram_transitions[k].get(key, 0) + (1 if success else 0)

    def record_outcome(self, action: str, hour: int, weekday: int, success: bool, persona: Optional[str] = None):
        persona = persona or "Idle"
        pm = self._pm(persona)
        self._ema_update(self.hour_hist[hour], action, 1.0 if success else 0.3)
        self._ema_update(self.weekday_hist[weekday], action, 1.0 if success else 0.3)
        self._ema_update(pm["hour_hist"][hour], action, 1.0 if success else 0.3)
        self._ema_update(pm["weekday_hist"][weekday], action, 1.0 if success else 0.3)

        # Trends: EWMA toward success ratio
        prev = self.trend.get(action, 0.5)
        target = 1.0 if success else 0.0
        self.trend[action] = (1 - self.trend_alpha) * prev + self.trend_alpha * target

        # Co-occurrence with last action
        if self.last_action:
            pair = (self.last_action, action)
            self.cooccur[pair] = self.cooccur.get(pair, 0) + 1
            tkey = f"{self.last_action}||{action}"
            self.transitions[tkey] = self.transitions.get(tkey, 0) + (1 if success else 0)

        self._update_kgrams(action, success)
        if success:
            self.bandit_alpha[action] = self.bandit_alpha.get(action, 1.0) + 1.0
        else:
            self.bandit_beta[action] = self.bandit_beta.get(action, 1.0) + 1.0
        delta = 0.08 if success else -0.06
        acc = self.memory.get_accuracy()
        acc_ratio = (acc["correct"] / max(1, acc["total"]))
        scale = 0.5 + 0.5 * acc_ratio
        self.action_weights[action] = min(1.2, max(0.0, self.action_weights.get(action, 0.5) + delta * scale))
        for k in self.novelty:
            self.novelty[k] = max(0.0, self.novelty[k] * 0.95)
        self.novelty[action] += 0.2 if success else 0.05
        self.cooldown[action] = min(1.0, self.cooldown.get(action, 0.0) + (0.2 if success else 0.05))
        for k in self.cooldown:
            self.cooldown[k] = max(0.0, self.cooldown[k] * 0.85)

        avg_w = sum(self.action_weights.values()) / max(1, len(self.action_weights))
        target = acc_ratio
        self.platt_A = 0.9 * self.platt_A + 0.1 * (target / max(1e-3, avg_w))
        self.platt_B = 0.9 * self.platt_B + 0.1 * (target - self.platt_A * avg_w)

        self.last_action = action
        self.last_action_ts = time.time()
        self.memory.set_weights(self.action_weights)
        self.memory.set_transitions(self.transitions)
        self.memory.record_outcome(action, success, {"hour": hour, "weekday": weekday, "persona": persona})
        self.memory.save()
        self.logger.log("learning", "Recorded outcome", {"action": action, "success": success, "persona": persona})

    def _time_bias(self, action: str, hour: int, weekday: int, persona: str) -> float:
        g_h = self.hour_hist[hour].get(action, 0.0)
        g_d = self.weekday_hist[weekday].get(action, 0.0)
        pm = self._pm(persona)
        p_h = pm["hour_hist"][hour].get(action, 0.0)
        p_d = pm["weekday_hist"][weekday].get(action, 0.0)
        g = min(1.0, g_h * 0.6 + g_d * 0.4)
        p = min(1.0, p_h * 0.6 + p_d * 0.4)
        return (1 - self.blend_lambda) * g + self.blend_lambda * p

    def _markov_bias(self, action: str) -> float:
        if not self.last_action:
            return 0.0
        tkey = f"{self.last_action}||{action}"
        return min(0.3, 0.02 * self.transitions.get(tkey, 0))

    def _cooccur_bias(self, action: str) -> float:
        if not self.last_action:
            return 0.0
        pair = (self.last_action, action)
        cnt = self.cooccur.get(pair, 0)
        return min(0.12, 0.03 * cnt)

    def _kgram_bias(self, action: str) -> float:
        seq = list(self.history)
        if not seq:
            return 0.0
        bias = 0.0
        weights = {2: 0.10, 3: 0.12, 4: 0.14, 5: 0.16}
        caps =   {2: 0.14, 3: 0.16, 4: 0.18, 5: 0.20}
        for k in range(2, self.k_max + 1):
            if len(seq) >= (k - 1):
                window = seq[-(k - 1):]
                key = self._kgram_key(window, next_action=action)
                count = self.kgram_transitions[k].get(key, 0)
                contrib = min(caps[k], weights[k] * count)
                bias += contrib
        return bias

    def _session_decay(self) -> float:
        if self.last_action_ts is None:
            return 0.0
        age = time.time() - self.last_action_ts
        return -0.05 if age > 300 else 0.0

    def _input_bias(self, action: str, input_state: Dict[str, Any]) -> float:
        kb = input_state.get("cadence_keyboard", 0.0)
        ms = input_state.get("cadence_mouse", 0.0)
        active = input_state.get("active", False)
        bias = 0.0
        if active:
            if kb > 0.6 and action in ("Open IDE", "Open Email"):
                bias += 0.15
            if ms > 0.6 and action == "Launch Browser":
                bias += 0.12
            if kb < 0.3 and ms < 0.3 and action == "Launch Steam":
                bias += 0.08
        return bias

    def _drive_net_bias(self, action: str, activity: Dict[str, Any]) -> float:
        status = activity.get("net", {}).get("status", "idle")
        total_drive_rw = sum((d["read_bps"] + d["write_bps"]) for d in activity.get("drives", {}).values()) if activity.get("drives") else 0.0
        up = activity.get("net", {}).get("up_bps", 0.0)
        down = activity.get("net", {}).get("down_bps", 0.0)
        conns = activity.get("net", {}).get("connections", 0)
        bias = 0.0
        if status == "gaming" and action == "Launch Steam":
            bias += 0.22
        if status == "browsing" and action == "Launch Browser":
            bias += 0.16
        if status == "transfer" and action in ("Open IDE", "Open Email"):
            bias += 0.08
        if total_drive_rw > 80_000_000 and action in ("Launch Steam", "Open IDE"):
            bias -= 0.07
        if conns > 25 and action == "Launch Steam":
            bias += 0.05
        if conns > 10 and down > 600_000 and action == "Launch Browser":
            bias += 0.05
        return bias

    def _web_hint_bias(self, action: str, web_hint: Dict[str, float]) -> float:
        bias = 0.0
        if action == "Launch Steam":
            bias += 0.18 * web_hint.get("gaming", 0.0)
        if action == "Launch Browser":
            bias += 0.16 * web_hint.get("browsing", 0.0)
        if action in ("Open IDE", "Open Email"):
            bias += 0.14 * web_hint.get("work", 0.0)
        if action in ("Open IDE", "Open Email") and web_hint.get("transfer", 0.0) > 0.4:
            bias += 0.06
        return bias

    def _feedback_bias(self, action: str) -> float:
        suppress, promote = self.memory.get_feedback()
        bias = 0.0
        if action in suppress or action in self.policy.suppress:
            bias -= 0.25
        if action in promote or action in self.policy.promote:
            bias += 0.25
        return bias

    def _novelty_boost(self, action: str) -> float:
        return min(0.08, 0.02 + 0.02 * (1.0 - min(1.0, self.novelty.get(action, 0.0))))

    def _persona_bias(self, action: str, persona: str) -> float:
        if persona == "Gaming" and action == "Launch Steam": return 0.22
        if persona == "Work" and action in ("Open IDE", "Open Email"): return 0.18
        if persona == "Browsing" and action == "Launch Browser": return 0.16
        return 0.0

    def _rhythm_bias(self, action: str, hour: int) -> float:
        rng = self.rhythm.get(action)
        if not rng: return 0.0
        start, end = rng
        in_range = start <= hour <= end
        return 0.1 if in_range else -0.06

    def _per_intent_accuracy_bias(self, action: str) -> float:
        pi = self.memory.state.get("per_intent", {}).get(action, {"correct": 0, "total": 0})
        ratio = pi["correct"] / max(1, pi["total"])
        return 0.12 * (ratio - 0.5)

    def _trend_bias(self, action: str) -> float:
        t = self.trend.get(action, 0.5)
        return 0.14 * (t - 0.5)

    def _adaptive_temperature(self, base_temp: float = 0.8) -> float:
        acc = self.memory.get_accuracy()
        acc_ratio = (acc["correct"] / max(1, acc["total"]))
        temp = base_temp - 0.3 * (acc_ratio - 0.5)
        return max(0.4, min(1.2, temp))

    def _calibrate_softmax(self, scores: List[float], temperature: float = 0.8) -> List[float]:
        exps = [math.exp(s / max(1e-6, temperature)) for s in scores]
        total = sum(exps) + 1e-9
        return [e / total for e in exps]

    def _platt_sigmoid(self, p: float) -> float:
        z = self.platt_A * p + self.platt_B
        return 1.0 / (1.0 + math.exp(-4.0 * (z - 0.5)))

    def _cluster(self, intent_id: str) -> str:
        return self.clusters.get(intent_id, "Other")

    def _diversify(self, intents: List[Intent], top_k: int = 4, max_per_cluster: int = 2, epsilon: float = 0.12) -> List[Intent]:
        selected: List[Intent] = []
        per_cluster_taken: Dict[str, int] = {}
        intents.sort(key=lambda i: i.calibrated, reverse=True)
        for intent in intents:
            c = intent.cluster or "Other"
            if per_cluster_taken.get(c, 0) < max_per_cluster:
                selected.append(intent)
                per_cluster_taken[c] = per_cluster_taken.get(c, 0) + 1
            if len(selected) >= top_k:
                break
        if len(selected) < top_k and intents:
            tail = intents[-1]
            if tail.id not in [i.id for i in selected]:
                flip = int(hashlib.sha256(str(time.time()).encode()).hexdigest(), 16) % 100
                if flip < int(epsilon * 100):
                    selected.append(tail)
        return selected

    def _attn_bias(self, action: str) -> float:
        seq = list(self.history)[-self.attn_window:]
        if not seq:
            return 0.0
        tgt = self.attn_keys.get(action, 0.5)
        sims = []
        for a in seq:
            sims.append(1.0 - abs(self.attn_keys.get(a, 0.5) - tgt))
        score = sum(sims) / max(1, len(sims))
        return min(self.attn_strength, 0.06 + 0.06 * score)

    def predict_with_temp(self, snapshot: Dict[str, Any], extra_temperature: float = 0.0) -> List[Intent]:
        hour = snapshot["hour"]
        weekday = snapshot["weekday"]
        input_state = snapshot.get("input_state", {})
        activity = snapshot.get("activity", {})
        persona = snapshot.get("persona", "Idle")
        web_hint = snapshot.get("web_hint", {})

        raw_scores: List[Tuple[str, float, Dict[str, Any]]] = []
        for action, base_w in self.action_weights.items():
            s_base = base_w
            s_time = 0.25 * self._time_bias(action, hour, weekday, persona)
            s_markov = self._markov_bias(action)
            s_kgram = self._kgram_bias(action)
            s_input = self._input_bias(action, input_state)
            s_ctx = self._drive_net_bias(action, activity)
            s_web = self._web_hint_bias(action, web_hint)
            s_co = self._cooccur_bias(action)
            s_feedback = self._feedback_bias(action)
            s_novelty = self._novelty_boost(action)
            s_session = self._session_decay()
            s_persona = self._persona_bias(action, persona)
            s_rhythm = self._rhythm_bias(action, hour)
            s_cooldown = -0.12 * self.cooldown.get(action, 0.0)
            s_piacc = self._per_intent_accuracy_bias(action)
            s_trend = self._trend_bias(action)
            a = self.bandit_alpha.get(action, 1.0)
            b = self.bandit_beta.get(action, 1.0)
            bandit_mean = a / max(1e-6, (a + b))
            s_bandit = 0.15 * (bandit_mean - 0.5)
            s_attn = self._attn_bias(action)

            score = (
                s_base + s_time + s_markov + s_kgram + s_input + s_ctx + s_web + s_co +
                s_feedback + s_novelty + s_session + s_persona + s_rhythm + s_cooldown +
                s_piacc + s_trend + s_bandit + s_attn
            )
            score = max(-1.0, min(2.0, score))
            evidence = {
                "base_weight": round(s_base, 3),
                "time_bias": round(s_time, 3),
                "markov_bias": round(s_markov, 3),
                "kgram_bias": round(s_kgram, 3),
                "input_bias": round(s_input, 3),
                "drive_net_bias": round(s_ctx, 3),
                "web_hint_bias": round(s_web, 3),
                "cooccur_bias": round(s_co, 3),
                "feedback_bias": round(s_feedback, 3),
                "novelty_boost": round(s_novelty, 3),
                "session_decay": round(s_session, 3),
                "persona_bias": round(s_persona, 3),
                "rhythm_bias": round(s_rhythm, 3),
                "cooldown_penalty": round(s_cooldown, 3),
                "per_intent_accuracy_bias": round(s_piacc, 3),
                "trend_bias": round(s_trend, 3),
                "bandit_mean": round(bandit_mean, 3),
                "bandit_bias": round(s_bandit, 3),
                "attn_bias": round(s_attn, 3),
                "persona": persona,
                "last_action": self.last_action,
                "context_status": activity.get("net", {}).get("status", "idle")
            }
            raw_scores.append((action, score, evidence))

        base_temp = self._adaptive_temperature(base_temp=0.78)
        temp = max(0.35, min(1.35, base_temp + extra_temperature))
        scores_only = [s for _, s, _ in raw_scores]
        probs = self._calibrate_softmax(scores_only, temperature=temp)
        probs = [self._platt_sigmoid(p) for p in probs]
        ssum = sum(probs) + 1e-9
        probs = [p / ssum for p in probs]

        intents: List[Intent] = []
        for idx, (action, score, evidence) in enumerate(raw_scores):
            c = self._cluster(action)
            intents.append(Intent(id=action, score=score, evidence=evidence, cluster=c, calibrated=probs[idx]))
        intents.sort(key=lambda i: i.calibrated, reverse=True)
        top_intents = self._diversify(intents, top_k=4, max_per_cluster=2, epsilon=0.12)
        self.logger.log("prediction", "Predicted intents (temp adj)", {"temperature": temp, "persona": persona, "intents": [asdict(i) for i in top_intents]})
        return top_intents

    def predict(self, snapshot: Dict[str, Any]) -> List[Intent]:
        return self.predict_with_temp(snapshot, extra_temperature=0.0)

# -------------------------------------------------------------------
# Dependency graph
# -------------------------------------------------------------------

class DependencyGraph:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.graph: Dict[str, List[str]] = {
            "EmailClient": ["TLSStack", "FontPack", "InboxCache", "AuthTokens"],
            "Browser": ["DNSCache", "TLSStack", "Extensions", "FontPack"],
            "TLSStack": ["CertStore"],
            "Extensions": ["AdBlock", "DarkMode"],
            "FontPack": ["Arial", "Roboto"],
            "Steam.exe": ["OverlayDLLs", "AntiCheatPassive", "ShaderCache"],
            "OverlayDLLs": ["HookLib"],
            "IDE": ["Compiler", "Debugger", "IndexCache", "LanguageServer"],
            "IndexCache": ["IndexShardA", "IndexShardB"],
        }
        self.hashes: Dict[str, str] = {}

    def resolve(self, nodes: List[str]) -> List[str]:
        resolved = set(nodes)
        frontier = list(nodes)
        while frontier:
            n = frontier.pop()
            for dep in self.graph.get(n, []):
                if dep not in resolved:
                    resolved.add(dep)
                    frontier.append(dep)
        return list(resolved)

    def verify(self, node: str) -> str:
        h = hashlib.sha256(node.encode("utf-8")).hexdigest()
        self.hashes[node] = h
        return h

    def next_dependencies(self, node: str, depth: int = 2) -> List[str]:
        seen = set(); result: List[str] = []
        def dfs(n: str, d: int):
            if d == 0 or n in seen: return
            seen.add(n)
            for dep in self.graph.get(n, []):
                result.append(dep); dfs(dep, d - 1)
        dfs(node, max(1, depth))
        return result

# -------------------------------------------------------------------
# Planner (chain widening with transitions + co-occurrence)
# -------------------------------------------------------------------

class Planner:
    def __init__(self, logger: Logger, capability: CapabilityProfiler, dep_graph: DependencyGraph, predictor: Optional[Predictor] = None):
        self.logger = logger
        self.capability = capability
        self.dep_graph = dep_graph
        self.predictor = predictor

    def _predict_chain(self, intent: Intent, max_len: int = 4) -> List[str]:
        chain = [intent.id]
        last = intent.id
        transitions = (self.predictor.transitions if self.predictor else {})
        co = (self.predictor.cooccur if self.predictor else {})
        for _ in range(max_len - 1):
            candidates = [(k.split("||")[1], v) for k, v in transitions.items() if k.startswith(last + "||")]
            # Blend with co-occurrence counts
            for a in set([c[0] for c in candidates]):
                pair = (last, a)
                if pair in co:
                    # boost candidate weight slightly
                    for i, (cid, w) in enumerate(candidates):
                        if cid == a:
                            candidates[i] = (cid, w + int(0.5 * co[pair]))
            if not candidates:
                break
            candidates.sort(key=lambda x: x[1], reverse=True)
            nxt = candidates[0][0]
            chain.append(nxt)
            last = nxt
        return chain

    def synthesize(self, intents: List[Intent]) -> Plan:
        profile = self.capability.get_profile()
        top = intents[0] if intents else Intent(id="Observe", score=0.0, evidence={}, calibrated=0.0)
        steps: List[PlanStep] = []
        now_str = datetime.datetime.now().isoformat()
        persona = top.evidence.get("persona", "Idle")
        rationale = f"[{now_str}] Plan for {top.id} ({persona}); disk={profile.scores['disk']:.2f}, gpu={profile.scores['gpu']:.2f}; confidence={top.calibrated:.2f}"

        if top.id == "Open Email":
            steps.append(PlanStep("Preload Email Bundle", deps=["EmailClient"], cost={"cpu": 0.12, "disk": 25e6, "mem": 256.0}, expected_gain_ms=900))
        elif top.id == "Launch Browser":
            steps.append(PlanStep("Preload Browser Bundle", deps=["Browser"], cost={"cpu": 0.15, "disk": 40e6, "mem": 384.0}, expected_gain_ms=1100))
        elif top.id == "Launch Steam":
            steps.append(PlanStep("Preload Steam Runtime", deps=["Steam.exe"], cost={"cpu": 0.18, "disk": 180e6, "mem": 512.0, "gpu_vram": 64.0}, expected_gain_ms=1400))
        elif top.id == "Open IDE":
            steps.append(PlanStep("Preload IDE Toolchain", deps=["IDE"], cost={"cpu": 0.16, "disk": 100e6, "mem": 512.0}, expected_gain_ms=1300))
        else:
            steps.append(PlanStep("Observe and Learn", deps=[], cost={"cpu": 0.02}, expected_gain_ms=0))

        chain = self._predict_chain(top, max_len=4)
        for act in chain[1:]:
            if act == "Launch Browser":
                steps.append(PlanStep("Speculative Browser Extensions", deps=["Extensions"], cost={"cpu":0.08,"disk":10e6,"mem":128.0}, expected_gain_ms=300))
            elif act == "Open IDE":
                steps.append(PlanStep("Speculative Index Cache", deps=["IndexCache"], cost={"cpu":0.10,"disk":45e6,"mem":256.0}, expected_gain_ms=420))
            elif act == "Launch Steam":
                steps.append(PlanStep("Speculative Shader Cache", deps=["ShaderCache"], cost={"cpu":0.10,"disk":80e6,"mem":256.0,"gpu_vram":64.0}, expected_gain_ms=500))
            elif act == "Open Email":
                steps.append(PlanStep("Speculative Inbox Cache", deps=["InboxCache"], cost={"cpu":0.06,"disk":8e6,"mem":128.0}, expected_gain_ms=260))

        if persona == "Work" and top.id == "Open IDE":
            steps[0].cost["disk"] *= 0.85
            steps[0].expected_gain_ms += 150
        if persona == "Gaming" and top.id == "Launch Steam":
            steps[0].cost["gpu_vram"] = steps[0].cost.get("gpu_vram", 0.0) + 128.0
            steps[0].expected_gain_ms += 220

        final_steps: List[PlanStep] = []
        for s in steps:
            deps_resolved = self.dep_graph.resolve(s.deps)
            disk_score = profile.scores.get("disk", 0.8)
            gain_adj = 1.0 + (disk_score - 0.5) * 0.6
            adjusted_gain = int(s.expected_gain_ms * gain_adj)
            final_steps.append(PlanStep(name=s.name, deps=deps_resolved, cost=s.cost, expected_gain_ms=adjusted_gain))

        expected_gain = sum(s.expected_gain_ms for s in final_steps)
        total_cost = {
            "cpu": sum(s.cost.get("cpu", 0.0) for s in final_steps),
            "disk": sum(s.cost.get("disk", 0.0) for s in final_steps),
            "mem": sum(s.cost.get("mem", 0.0) for s in final_steps),
            "gpu_vram": sum(s.cost.get("gpu_vram", 0.0) for s in final_steps),
        }

        plan = Plan(
            id=f"plan_{int(time.time())}",
            steps=final_steps,
            total_cost=total_cost,
            expected_gain_ms=expected_gain,
            rationale=rationale,
            chosen_intent=top
        )
        self.logger.log("planning", "Synthesized plan", {"plan": asdict(plan), "chain": chain})
        return plan

# -------------------------------------------------------------------
# Policy engine (confidence-weighted autonomy)
# -------------------------------------------------------------------

class PolicyEngine:
    def __init__(self, logger: Logger, policy: Policy, capability: CapabilityProfiler):
        self.logger = logger
        self.policy = policy
        self.capability = capability

    def evaluate(self, plan: Plan, snapshot: Dict[str, Any]) -> Decision:
        hour = snapshot["hour"]
        start, end = self.policy.quiet_hours
        in_quiet = (start <= hour <= end) if start <= end else (hour >= start or hour <= end)

        cpu_ok = plan.total_cost.get("cpu", 0.0) <= self.policy.cpu_cap
        disk_ok = plan.total_cost.get("disk", 0.0) <= self.policy.disk_cap_bps * 2
        vram_ok = plan.total_cost.get("gpu_vram", 0.0) <= self.policy.vram_cap_mb

        conf = (plan.chosen_intent.calibrated if plan.chosen_intent else 0.0)
        if conf > 0.58:
            autonomy = "act"
        elif conf > 0.36:
            autonomy = "suggest"
        else:
            autonomy = "log"

        allow = (autonomy == "act") and cpu_ok and disk_ok and vram_ok and not in_quiet
        notify = True if autonomy != "act" else (self.policy.autonomy_level != "background")
        rationale = f"autonomy={autonomy}, conf={conf:.2f}, cpu_ok={cpu_ok}, disk_ok={disk_ok}, vram_ok={vram_ok}, in_quiet={in_quiet}"
        risk = "low" if allow else ("medium" if autonomy == "suggest" else "low")
        decision = Decision(allow=allow, notify=notify, rationale=rationale, risk=risk, policy_gate=asdict(self.policy))
        self.logger.log("policy", "Policy decision", {"decision": asdict(decision)})
        return decision

# -------------------------------------------------------------------
# Auto-loader (capability-aware prefetch scaling)
# -------------------------------------------------------------------

class AutoLoader:
    def __init__(self, logger: Logger, dep_graph: DependencyGraph, capability: CapabilityProfiler, read_ahead_window: int = 2):
        self.logger = logger
        self.dep_graph = dep_graph
        self.capability = capability
        self.read_ahead_window = max(0, read_ahead_window)

    def _strategy(self, plan: Plan, snapshot: Optional[Dict[str, Any]] = None) -> str:
        prof = self.capability.get_profile()
        disk = prof.scores.get("disk", 0.8)
        mem = prof.scores.get("mem", 0.7)
        gpu = prof.scores.get("gpu", 0.5)
        gpu_vendor = snapshot.get("gpu", {}).get("vendor") if snapshot else None
        if plan.total_cost.get("gpu_vram", 0.0) > 0 and gpu > 0.65 and gpu_vendor:
            return "gpu_vram_staging"
        if disk > mem:
            return "disk_prefetch"
        return "balanced"

    def _adjust_read_ahead(self, snapshot: Optional[Dict[str, Any]]) -> int:
        window = self.read_ahead_window
        if not snapshot:
            return window
        mem_free_mb = snapshot.get("mem_free_mb", 512.0)
        cpu_util = snapshot.get("cpu_util", 50.0)
        if mem_free_mb < 1024.0 or cpu_util > 80.0:
            window = max(1, window - 1)
        if mem_free_mb > 4096.0 and cpu_util < 40.0:
            window = min(window + 1, 4)
        return window

    def execute(self, plan: Plan, snapshot: Optional[Dict[str, Any]] = None) -> Result:
        strategy = self._strategy(plan, snapshot)
        verified = {}
        resources = plan.total_cost.copy()
        loaded = set()

        conf = plan.chosen_intent.calibrated if plan.chosen_intent else 0.0
        prof = self.capability.get_profile()
        scale = 1.0 + 0.5 * (conf - 0.5) + 0.3 * (prof.scores.get("disk",0.6) - 0.5)
        scale = max(0.6, min(1.6, scale))

        for step in plan.steps:
            for d in step.deps:
                verified[d] = self.dep_graph.verify(d)
                loaded.add(d)
            time.sleep(0.05 * (2.0 - scale))
            self.logger.log("preload", f"Executed '{step.name}'", {"deps": step.deps, "strategy": strategy, "cost": step.cost, "scale": round(scale,3)})

        top_intent_id = plan.chosen_intent.id if plan.chosen_intent else None
        if top_intent_id:
            window = self._adjust_read_ahead(snapshot)
            next_deps = self.dep_graph.next_dependencies(top_intent_id, depth=window)
            for dep in next_deps:
                if dep in loaded:
                    self.logger.log("speculative", f"Skipped speculative preload of '{dep}' (already loaded)", {"source": top_intent_id, "window": window})
                    continue
                verified[dep] = self.dep_graph.verify(dep)
                time.sleep(0.01 * (2.0 - scale))
                loaded.add(dep)
                self.logger.log("speculative", f"Speculative preload of '{dep}'", {"source": top_intent_id, "window": window, "scale": round(scale,3)})
        return Result(success=True, resources=resources, verified_hashes=verified, notes=f"Preload via {strategy} with read-ahead and scale {round(scale,3)}")

# -------------------------------------------------------------------
# Self-improver
# -------------------------------------------------------------------

class SelfImprover:
    def __init__(self, logger: Logger, crypto: CryptoManager, policy: UpdatePolicy, project_root: str, version_file: str = "VERSION"):
        self.logger = logger
        self.crypto = crypto
        self.policy = policy
        self.project_root = os.path.abspath(project_root)
        self.version_file = os.path.join(self.project_root, version_file)

    def _now_hour(self) -> int:
        return datetime.datetime.now().hour

    def _in_quiet(self) -> bool:
        s, e = self.policy.quiet_hours
        return s <= self._now_hour() <= e if s <= e else (self._now_hour() >= s or self._now_hour() <= e)

    def _allowed(self, path: str) -> bool:
        ap = os.path.abspath(path)
        for allowed in self.policy.allow_paths:
            if ap.startswith(os.path.abspath(os.path.join(self.project_root, allowed))):
                return True
        return False

    def _all_py_files(self) -> List[str]:
        files = []
        for root, _, names in os.walk(self.project_root):
            for n in names:
                if n.endswith(".py"):
                    files.append(os.path.join(root, n))
        return files

    def _lint(self) -> bool:
        if not self.policy.require_lint_pass:
            return True
        try:
            result = subprocess.run(["python", "-m", "py_compile"] + self._all_py_files(), capture_output=True, text=True)
            ok = result.returncode == 0
            self.logger.log("selfimprove", "Lint/compile check", {"ok": ok, "stderr": result.stderr[:500]})
            return ok
        except Exception as e:
            self.logger.log("selfimprove", "Lint error", {"error": str(e)})
            return False

    def _tests(self) -> bool:
        if not self.policy.require_tests_pass:
            return True
        try:
            result = subprocess.run(["python", "-m", "pytest", "-q"], cwd=self.project_root, capture_output=True, text=True)
            ok = result.returncode == 0
            self.logger.log("selfimprove", "Tests run", {"ok": ok, "stdout": result.stdout[:500], "stderr": result.stderr[:500]})
            return ok
        except Exception as e:
            self.logger.log("selfimprove", "Tests error", {"error": str(e)})
            return False

    def _sandbox_import(self, candidate_paths: List[str]) -> bool:
        for p in candidate_paths:
            if not p.endswith(".py"): continue
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ft_sandbox_" + hashlib.md5(p.encode()).hexdigest(), p)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
            except Exception as e:
                self.logger.log("selfimprove", "Sandbox import failed", {"path": p, "error": str(e)})
                return False
        return True

    def _bump_version(self) -> str:
        old = "0.0.0"
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, "r", encoding="utf-8") as f:
                    old = f.read().strip()
            major, minor, patch = [int(x) for x in old.split(".")]
            new = f"{major}.{minor}.{patch+1}"
        except Exception:
            new = "0.0.1"
        with open(self.version_file, "w", encoding="utf-8") as f:
            f.write(new)
        return new

    def propose_patches(self, signals: Dict[str, int]) -> List[Patch]:
        patches: List[Patch] = []
        target = os.path.join(self.project_root, "fortune_teller.py")
        if signals.get("serialization_errors", 0) > 0:
            fix = "# Self-improver: enforce asdict() usage for dataclass serialization\n"
            patches.append(Patch(target_path=target, description="Serialization hardening", diff=fix, bytes=len(fix)))
        if signals.get("policy_deferrals", 0) > 3:
            fix = "# Self-improver: auto-tune policy cpu_cap (suggest +0.05 up to 0.8)\n"
            patches.append(Patch(target_path=target, description="Policy auto-tuning", diff=fix, bytes=len(fix)))
        if signals.get("gpu_stalls", 0) > 2:
            fix = "# Self-improver: prefer gpu_vram_staging when GPU score > 0.65 and disk score > 0.7\n"
            patches.append(Patch(target_path=target, description="GPU staging improvements", diff=fix, bytes=len(fix)))
        return patches

    def apply_patches(self, patches: List[Patch]) -> UpdateResult:
        if not patches:
            return UpdateResult(False, "No patches proposed", [], [], "")
        if self._in_quiet():
            return UpdateResult(False, "Deferred: quiet hours", [], [], "")
        files_changed, backups = [], []
        for p in patches:
            if not self._allowed(p.target_path):
                return UpdateResult(False, f"Disallowed path: {p.target_path}", [], [], "")
            if p.bytes > self.policy.max_patch_bytes:
                return UpdateResult(False, "Patch too large", [], [], "")
        for p in patches:
            if self.policy.create_backup and os.path.exists(p.target_path):
                backup = p.target_path + f".bak.{int(time.time())}"
                import shutil
                shutil.copy2(p.target_path, backup)
                backups.append(backup)
            note_path = p.target_path + ".patchlog.enc"
            try:
                payload = {"ts": datetime.datetime.utcnow().isoformat(),
                           "target": p.target_path,
                           "desc": p.description,
                           "diff": p.diff,
                           "sig": self.crypto.sign_text(p.diff)}
                raw = json.dumps(payload).encode("utf-8")
                enc = self.crypto.encrypt(raw, aad=b"fortune_teller_patch")
                with open(note_path, "ab") as nf:
                    nf.write(enc + b"\n")
            except Exception:
                pass
            with open(p.target_path, "a", encoding="utf-8") as f:
                f.write("\n" + p.diff + "\n")
            files_changed.append(p.target_path)
        if not self._lint():
            self._rollback(backups)
            return UpdateResult(False, "Lint failed; rolled back", [], backups, "")
        if not self._tests():
            self._rollback(backups)
            return UpdateResult(False, "Tests failed; rolled back", [], backups, "")
        if not self._sandbox_import(files_changed):
            self._rollback(backups)
            return UpdateResult(False, "Import failed; rolled back", [], backups, "")
        signature = hashlib.sha256(("".join(files_changed) + str(time.time())).encode()).hexdigest()
        new_version = self._bump_version()
        self.logger.log("selfimprove", "Applied patches", {"files": files_changed, "version": new_version, "signature": signature})
        return UpdateResult(True, "Patches applied", files_changed, backups, signature, version=new_version)

    def _rollback(self, backups: List[str]):
        import shutil
        for b in backups:
            orig = b.split(".bak.")[0]
            try:
                shutil.copy2(b, orig)
                self.logger.log("selfimprove", "Rolled back file", {"file": orig})
            except Exception as e:
                self.logger.log("selfimprove", "Rollback failed", {"backup": b, "error": str(e)})

# -------------------------------------------------------------------
# Orchestrator (adaptive exploration via entropy + anomaly)
# -------------------------------------------------------------------

class Orchestrator:
    def __init__(self, logger: Logger, telemetry: TelemetryCollector,
                 predictor: Predictor, planner: Planner,
                 policy: PolicyEngine, autoloader: AutoLoader,
                 improver: SelfImprover, anomaly: AnomalyDetector,
                 mesh_bundle: Dict[str, Any]):
        self.logger = logger
        self.telemetry = telemetry
        self.predictor = predictor
        self.planner = planner
        self.policy = policy
        self.autoloader = autoloader
        self.improver = improver
        self.anomaly = anomaly
        self.mesh_bundle = mesh_bundle
        self.stop_flag = False
        self._last_improve_day: Optional[int] = None
        self.last_snapshot: Optional[Dict[str, Any]] = None
        self.last_intents: Optional[List[Intent]] = None
        self.last_plan: Optional[Plan] = None
        self.last_decision: Optional[Decision] = None
        self.last_result: Optional[Result] = None

    def start(self, interval_sec: float = 5.0):
        threading.Thread(target=self._loop, args=(interval_sec,), daemon=True).start()
        self.logger.log("orchestrator", "Autonomy loop started", {"interval_sec": interval_sec})

    def _improve_daily(self):
        today = datetime.datetime.now().timetuple().tm_yday
        if self._last_improve_day == today:
            return
        self._last_improve_day = today
        signals = {
            "serialization_errors": self.logger.count("error"),
            "policy_deferrals": self.logger.count("policy_defer"),
            "gpu_stalls": self.logger.count("gpu_stall"),
        }
        patches = self.improver.propose_patches(signals)
        result = self.improver.apply_patches(patches)
        self.logger.log("selfimprove", "Daily self-improvement", asdict(result))

    def _entropy(self, probs: List[float]) -> float:
        s = sum(probs)
        ps = [p / s for p in probs] if s > 0 else probs
        return -sum(p * math.log(p + 1e-9) for p in ps)

    def _loop(self, interval_sec: float):
        mesh_in: queue.Queue = self.mesh_bundle["in_q"]
        while not self.stop_flag:
            snap = self.telemetry.snapshot()
            self.last_snapshot = snap

            intents_pass1 = self.predictor.predict_with_temp(snap, extra_temperature=0.0)
            probs = [i.calibrated for i in intents_pass1[:4]] if intents_pass1 else []
            entropy = self._entropy(probs) if probs else 0.0
            anomalies_active = bool(self.anomaly.observe(snap).get("active"))
            exploratory = anomalies_active or entropy > 1.1
            temp_boost = 0.18 if exploratory else 0.0

            intents = self.predictor.predict_with_temp(snap, extra_temperature=temp_boost)
            self.last_intents = intents
            plan = self.planner.synthesize(intents)
            self.last_plan = plan
            decision = self.policy.evaluate(plan, snap)
            self.last_decision = decision

            persona = snap.get("persona", "Idle")
            if decision.allow:
                result = self.autoloader.execute(plan, snapshot=snap)
                self.last_result = result
                success = True
                self.predictor.record_outcome(plan.chosen_intent.id if plan.chosen_intent else "Observe",
                                              snap["hour"], snap["weekday"], success=success, persona=persona)
                self.logger.log("orchestrator", "Executed plan", {"plan": asdict(plan), "result": asdict(result)})
            else:
                self.last_result = None
                success = False
                self.predictor.record_outcome(plan.chosen_intent.id if plan.chosen_intent else "Observe",
                                              snap["hour"], snap["weekday"], success=success, persona=persona)
                self.logger.log("policy_defer", "Plan deferred", {"decision": asdict(decision)})

            if persona == "Browsing":
                mesh_in.put(MeshEvent(url="https://example.com", snippet="Browsing context", links=["https://example.com/about"]))
            self._improve_daily()
            time.sleep(interval_sec)

    def stop(self):
        self.stop_flag = True
        self.logger.log("orchestrator", "Autonomy loop stopped")

# -------------------------------------------------------------------
# GUI Manager — tabs only, autonomous (no manual feedback/persona)
# -------------------------------------------------------------------

class GUIManager:
    def __init__(self, predictor: Predictor, telemetry: TelemetryCollector,
                 logger: Logger, memory: MemoryManager, mesh: BorgMesh,
                 orchestrator: Orchestrator, capability: CapabilityProfiler,
                 policy_engine: PolicyEngine):
        self.predictor = predictor
        self.telemetry = telemetry
        self.logger = logger
        self.memory = memory
        self.mesh = mesh
        self.orchestrator = orchestrator
        self.capability = capability
        self.policy_engine = policy_engine
        if TK_AVAILABLE:
            self.root = tk.Tk()
            self.root.title("Fortune Teller — Autonomous (Network/Web)")
            self.nb = ttk.Notebook(self.root)
            self.nb.pack(fill="both", expand=True)
            self._setup_gui()
            threading.Thread(target=self._refresh_loop, daemon=True).start()

    def _setup_tab(self, name: str, height: int = 14):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text=name)
        text = tk.Text(frame, height=height)
        text.pack(fill="both", expand=True)
        return frame, text

    def _setup_gui(self):
        self.pred_frame, self.pred_text = self._setup_tab("Predictor", 14)
        self.mesh_frame, self.mesh_text = self._setup_tab("Borg Mesh", 14)
        self.logs_frame, self.logs_text = self._setup_tab("Logs", 18)
        self.telemetry_frame, self.telemetry_text = self._setup_tab("Telemetry", 20)
        self.policy_frame, self.policy_text = self._setup_tab("Policy", 14)
        self.planner_frame, self.planner_text = self._setup_tab("Planner", 16)
        self.loader_frame, self.loader_text = self._setup_tab("AutoLoader", 14)
        self.cap_frame, self.cap_text = self._setup_tab("Capability", 14)

    def _refresh_loop(self):
        while True:
            self._refresh_ui()
            time.sleep(12.0)

    def _refresh_ui(self):
        try:
            intents = self.orchestrator.last_intents or []
            self.pred_text.delete("1.0", tk.END)
            self.pred_text.insert(tk.END, json.dumps([asdict(i) for i in intents], indent=2))

            mstats = self.mesh.stats()
            sample_nodes = dict(list(self.mesh.nodes.items())[:50])
            self.mesh_text.delete("1.0", tk.END)
            self.mesh_text.insert(tk.END, json.dumps({"stats": mstats, "sample": sample_nodes}, indent=2))

            for evt in self.logger.drain(120):
                self.logs_text.insert(tk.END, f"{evt['ts']} [{evt['kind']}] {evt['message']} {json.dumps(evt['meta'])}\n")
            self.logs_text.see(tk.END)

            snap = self.orchestrator.last_snapshot or self.telemetry.snapshot()
            safe_snap = dict(snap)
            safe_snap["disk_io"] = {k: v for k, v in (safe_snap.get("disk_io") or {}).items()}
            safe_snap["net_io"] = {k: v for k, v in (safe_snap.get("net_io") or {}).items()}
            self.telemetry_text.delete("1.0", tk.END)
            self.telemetry_text.insert(tk.END, json.dumps(safe_snap, indent=2))

            decision = self.orchestrator.last_decision
            policy_view = {
                "policy": asdict(self.policy_engine.policy),
                "last_decision": asdict(decision) if decision else None,
            }
            self.policy_text.delete("1.0", tk.END)
            self.policy_text.insert(tk.END, json.dumps(policy_view, indent=2))

            plan = self.orchestrator.last_plan
            self.planner_text.delete("1.0", tk.END)
            self.planner_text.insert(tk.END, json.dumps(asdict(plan) if plan else {"plan": None}, indent=2))

            result = self.orchestrator.last_result
            self.loader_text.delete("1.0", tk.END)
            self.loader_text.insert(tk.END, json.dumps(asdict(result) if result else {"result": None}, indent=2))

            profile = self.capability.get_profile()
            self.cap_text.delete("1.0", tk.END)
            self.cap_text.insert(tk.END, json.dumps(asdict(profile), indent=2))

        except Exception as e:
            try:
                self.logs_text.insert(tk.END, f"{datetime.datetime.utcnow().isoformat()} [gui_error] {str(e)}\n")
            except Exception:
                pass

    def run(self):
        if TK_AVAILABLE:
            self.root.mainloop()

# -------------------------------------------------------------------
# build_system and main
# -------------------------------------------------------------------

def build_system(project_root: str = ".", iface_cidr: Optional[str] = None) -> Dict[str, Any]:
    crypto = CryptoManager()
    memory = MemoryManager(crypto)
    logger = Logger(crypto)
    input_monitor = InputMonitor(logger)
    activity = ActivityAnalyzer(logger)
    telemetry = TelemetryCollector(logger, input_monitor, activity)
    capability = CapabilityProfiler(logger, telemetry)
    dep_graph = DependencyGraph(logger)
    policy = Policy(
        autonomy_level="background",
        cpu_cap=0.5,
        disk_cap_bps=150e6,
        vram_cap_mb=1024.0,
        quiet_hours=(1, 6),
        privacy_scopes={"exclude_paths": ["C:/Sensitive", "/home/private"], "exclude_processes": ["BankApp"]},
        assist_not_act=True,
        suppress=[],
        promote=[]
    )
    predictor = Predictor(logger, memory, policy)
    planner = Planner(logger, capability, dep_graph, predictor=predictor)
    policy_engine = PolicyEngine(logger, policy, capability)
    autoloader = AutoLoader(logger, dep_graph, capability, read_ahead_window=2)
    anomaly = AnomalyDetector(logger)

    update_policy = UpdatePolicy(
        allow_paths=["."],
        max_patch_bytes=4096,
        quiet_hours=(1, 6),
        require_tests_pass=False,
        require_lint_pass=True,
        create_backup=True
    )
    improver = SelfImprover(logger, crypto, update_policy, project_root=project_root)

    comms = BorgCommsRouter(logger)
    guardian = SecurityGuardian(logger)
    mesh = BorgMesh(memory, comms, guardian)
    mesh_in = queue.Queue()
    mesh_ops = queue.Queue()
    scanner = BorgScanner(mesh, mesh_in, mesh_ops, label="SCANNER-1")
    worker = BorgWorker(mesh, mesh_ops, label="WORKER-1")
    enforcer = BorgEnforcer(mesh, guardian, label="ENFORCER-1")
    scanner.start(); worker.start(); enforcer.start()

    orchestrator = Orchestrator(logger, telemetry, predictor, planner, policy_engine, autoloader, improver, anomaly,
                                mesh_bundle={"mesh": mesh, "scanner": scanner, "worker": worker, "enforcer": enforcer, "in_q": mesh_in, "ops_q": mesh_ops})

    return {
        "crypto": crypto,
        "memory": memory,
        "logger": logger,
        "input_monitor": input_monitor,
        "activity": activity,
        "telemetry": telemetry,
        "capability": capability,
        "dep_graph": dep_graph,
        "policy": policy,
        "predictor": predictor,
        "planner": planner,
        "policy_engine": policy_engine,
        "autoloader": autoloader,
        "anomaly": anomaly,
        "improver": improver,
        "borg": {"mesh": mesh, "scanner": scanner, "worker": worker, "enforcer": enforcer, "in_q": mesh_in, "ops_q": mesh_ops},
        "orchestrator": orchestrator,
    }

def main(cli_mode: Optional[bool] = None, iface_cidr: Optional[str] = None):
    ok = ensure_admin_once()
    if not ok:
        return

    if cli_mode is None:
        cli_mode = HEADLESS_MODE

    system = build_system(project_root=".", iface_cidr=iface_cidr)
    logger: Logger = system["logger"]
    input_monitor: InputMonitor = system["input_monitor"]
    telemetry: TelemetryCollector = system["telemetry"]
    capability: CapabilityProfiler = system["capability"]
    predictor: Predictor = system["predictor"]
    planner: Planner = system["planner"]
    policy_engine: PolicyEngine = system["policy_engine"]
    autoloader: AutoLoader = system["autoloader"]
    orchestrator: Orchestrator = system["orchestrator"]
    memory: MemoryManager = system["memory"]
    mesh: BorgMesh = system["borg"]["mesh"]

    input_monitor.start()
    telemetry.start()
    capability.run_probes()
    orchestrator.start(interval_sec=5.0)

    borg_bundle = system["borg"]
    mesh_in: queue.Queue = borg_bundle["in_q"]
    seed_events = [
        MeshEvent(url="https://example.com", snippet="Landing page with http links", links=["https://example.com/about", "https://example.com/docs"]),
        MeshEvent(url="https://example.org", snippet="API docs token placeholder", links=["https://example.org/api", "https://example.org/changelog"]),
        MeshEvent(url="https://store.steampowered.com", snippet="Steam Store browsing", links=["https://store.steampowered.com/app/123", "https://store.steampowered.com/search/"])
    ]
    for ev in seed_events:
        mesh_in.put(ev)

    now = datetime.datetime.now()
    predictor.record_outcome("Launch Steam", now.hour, now.weekday(), success=True, persona="Gaming")
    predictor.record_outcome("Open IDE", now.hour, now.weekday(), success=False, persona="Work")

    if not cli_mode and TK_AVAILABLE:
        gui = GUIManager(predictor, telemetry, logger, memory, mesh, orchestrator=orchestrator, capability=capability, policy_engine=policy_engine)
        gui.run()
    else:
        mode = "CLI (headless)" if HEADLESS_MODE else "CLI (requested)"
        logger.log("system", f"Running Fortune Teller in {mode}")
        try:
            for _ in range(8):
                time.sleep(2.0)
                for evt in logger.drain():
                    print(f"{evt['ts']} [{evt['kind']}] {evt['message']} {json.dumps(evt['meta'])}")
        finally:
            telemetry.stop()
            input_monitor.stop()
            orchestrator.stop()
            try:
                borg_bundle["scanner"].stop()
                borg_bundle["worker"].stop()
                borg_bundle["enforcer"].stop()
            except Exception:
                pass

if __name__ == "__main__":
    print("Starting Fortune Teller (autonomous, network/web‑aware, attention, persona‑conditioned, chain planning)...")
    if "--cli" in sys.argv:
        main(cli_mode=True, iface_cidr=None)
    else:
        main(cli_mode=None, iface_cidr=None)

