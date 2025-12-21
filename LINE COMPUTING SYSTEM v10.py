# ============================================================
# LINE COMPUTING SYSTEM v8
# Engine + GUI + watchdog + swarm + system backplane
# + profiling + per-process whitelist/blacklist
# + profile metadata + strict mode + action policies
# + heavy predictive engine (temporal memory, drift, operator modeling)
# + HYBRID ALLOW-FOLDING (auto, threshold, manual, never-fold)
# ============================================================

# -----------------------------
# AUTO-LOAD REQUIRED LIBRARIES
# -----------------------------
import importlib

required_libs = [
    "time", "logging", "json", "os", "random",
    "threading", "queue", "tkinter", "tkinter.scrolledtext",
    "subprocess", "socket"
]

for lib in required_libs:
    parts = lib.split(".")
    module = importlib.import_module(lib)
    if len(parts) == 1:
        globals()[lib] = module
    else:
        globals()[parts[-1]] = module

# Optional psutil for deeper system hooks
try:
    psutil = importlib.import_module("psutil")
except ImportError:
    psutil = None

# -----------------------------
# GLOBAL CONSTANTS
# -----------------------------
SETTINGS_FILE = "line_settings.json"

SYMBOL_OK = "✔"
SYMBOL_BAD = "✖"
SYMBOL_SYNC = "⇆"
SYMBOL_THREAT = "⚠"
SYMBOL_WATCHDOG = "👁"
SYMBOL_SYS = "⭑"
SYMBOL_PROFILE = "◆"
SYMBOL_STRICT = "⛔"
SYMBOL_PRED = "♜"
SYMBOL_FOLD = "➕"

# -----------------------------
# SETTINGS MEMORY
# -----------------------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "expected_sequence": ["LEFT", "RIGHT"],
        "profile_sequence": [],
        "profile_metadata": {},
        "swarm_nodes": 3,
        "event_interval": 0.5,
        "watchdog_timeout": 5.0,
        "system_poll_interval": 2.0,
        "process_whitelist": [],
        "process_blacklist": [],
        "process_policies": {
            # "PROCESSNAME.EXE": "allow" | "log" | "alert" | "kill" | "ignore"
        },
        "strict_mode": False,
        "predictive": {
            "risk_threshold_strict": 70,
            "risk_threshold_warn": 40
        },
        "folding": {
            "unknown_threshold": 5  # N = 5, cautious
        }
    }

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass

settings = load_settings()

# -----------------------------
# EVENT BUS (PUB/SUB)
# -----------------------------
class EventBus:
    def __init__(self):
        self.subscribers = {}
        self.lock = threading.Lock()

    def subscribe(self, event_type, callback):
        with self.lock:
            self.subscribers.setdefault(event_type, []).append(callback)

    def publish(self, event_type, data=None):
        with self.lock:
            callbacks = list(self.subscribers.get(event_type, []))
        for cb in callbacks:
            try:
                cb(event_type, data)
            except Exception as e:
                logging.error(f"EventBus error: {e}")

event_bus = EventBus()

# -----------------------------
# LIVE LOG BUFFER
# -----------------------------
class LiveLog:
    def __init__(self, max_entries=500):
        self.buffer = []
        self.max_entries = max_entries
        self.lock = threading.Lock()

    def add(self, level, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} | {level} | {msg}"
        with self.lock:
            print(entry)
            self.buffer.append(entry)
            if len(self.buffer) > self.max_entries:
                self.buffer.pop(0)
        event_bus.publish("log", entry)

    def dump(self):
        with self.lock:
            return "\n".join(self.buffer)

log = LiveLog()

# -----------------------------
# THREAT MATRIX
# -----------------------------
class ThreatMatrix:
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()

    def record(self, event, expected, source="line", action=None, score=None):
        with self.lock:
            self.events.append({
                "event": event,
                "expected": expected,
                "source": source,
                "action": action,
                "score": score,
                "timestamp": time.time()
            })
        extra = ""
        if action:
            extra += f" action={action}"
        if score is not None:
            extra += f" score={score:.1f}"
        glyph = f"{SYMBOL_THREAT} [{source}] {event} (expected {expected}){extra}"
        event_bus.publish("threat", glyph)

    def summary(self):
        with self.lock:
            lines = []
            for e in self.events:
                extra = ""
                if e.get("action"):
                    extra += f" action={e['action']}"
                if e.get("score") is not None:
                    extra += f" score={e['score']:.1f}"
                lines.append(
                    f"{SYMBOL_THREAT} [{e['source']}] {e['event']} (expected {e['expected']}){extra}"
                )
            return lines

threat_matrix = ThreatMatrix()

# -----------------------------
# PREDICTIVE ENGINE
# -----------------------------
class PredictiveEngine:
    def __init__(self, config):
        self.lock = threading.Lock()
        self.temporal_events = {}      # hour -> event -> count
        self.anomaly_history = []      # (ts, event, score)
        self.operator_activity = {}    # hour -> weight
        self.current_risk = 0.0

        self.risk_threshold_warn = config.get("risk_threshold_warn", 40)
        self.risk_threshold_strict = config.get("risk_threshold_strict", 70)

    def _get_hour_bucket(self, ts=None):
        if ts is None:
            ts = time.time()
        lt = time.localtime(ts)
        return lt.tm_hour

    def observe_event(self, event_type, source, is_anomaly=False):
        now = time.time()
        hour = self._get_hour_bucket(now)

        with self.lock:
            self.temporal_events.setdefault(hour, {})
            self.temporal_events[hour][event_type] = self.temporal_events[hour].get(event_type, 0) + 1
            self.operator_activity[hour] = self.operator_activity.get(hour, 0) + 1

            rarity_score = self._compute_rarity(event_type, hour)

            if is_anomaly:
                base = 30.0
            else:
                base = 5.0

            delta = base + rarity_score
            tod_weight = self._time_of_day_weight(hour)
            delta *= tod_weight

            if not is_anomaly:
                delta = -min(delta, 5.0)

            self.current_risk *= 0.97
            self.current_risk += delta
            self.current_risk = max(0.0, min(100.0, self.current_risk))

            if is_anomaly:
                self.anomaly_history.append((now, event_type, self.current_risk))
                if len(self.anomaly_history) > 1000:
                    self.anomaly_history.pop(0)

            risk = self.current_risk

        event_bus.publish("predictive_risk", {"risk": risk})
        return risk

    def _compute_rarity(self, event_type, hour):
        hour_map = self.temporal_events.get(hour, {})
        total = sum(hour_map.values())
        if total == 0:
            return 5.0
        freq = hour_map.get(event_type, 0)
        p = freq / max(total, 1)
        if p > 0.2:
            return 0.0
        elif p > 0.05:
            return 5.0
        elif p > 0.01:
            return 10.0
        else:
            return 20.0

    def _time_of_day_weight(self, hour):
        total_activity = sum(self.operator_activity.values()) or 1
        this_activity = self.operator_activity.get(hour, 0)
        activity_ratio = this_activity / total_activity

        if activity_ratio < 0.02:
            return 2.0
        elif activity_ratio < 0.05:
            return 1.5
        elif activity_ratio < 0.15:
            return 1.2
        else:
            return 1.0

    def get_risk(self):
        with self.lock:
            return self.current_risk

    def classify_risk_level(self):
        r = self.get_risk()
        if r >= self.risk_threshold_strict:
            return "HIGH"
        elif r >= self.risk_threshold_warn:
            return "WARN"
        else:
            return "NORMAL"

predictive_engine = PredictiveEngine(settings.get("predictive", {}))

# -----------------------------
# LINE COMPUTING ENGINE
# -----------------------------
class LineComputer:
    def __init__(self, expected_sequence, strict_mode=False):
        self.expected = expected_sequence
        self.index = 0
        self.lock = threading.Lock()
        self.last_event_time = time.time()
        self.strict_mode = strict_mode

    def set_expected_sequence(self, sequence):
        with self.lock:
            self.expected = list(sequence)
            self.index = 0
        log.add("INFO", f"{SYMBOL_PROFILE} Expected sequence updated. Length={len(sequence)}")
        event_bus.publish("line_updated", {"expected_sequence": list(sequence)})

    def get_expected_sequence(self):
        with self.lock:
            return list(self.expected)

    def set_strict_mode(self, enabled: bool):
        with self.lock:
            self.strict_mode = enabled
        mode_str = "ON" if enabled else "OFF"
        log.add("INFO", f"{SYMBOL_STRICT} Strict mode {mode_str}.")
        settings["strict_mode"] = enabled
        save_settings(settings)

    def is_strict_mode(self):
        with self.lock:
            return self.strict_mode

    def process(self, event, source="line"):
        with self.lock:
            if not self.expected:
                expected_event = None
            else:
                expected_event = self.expected[self.index]
            self.last_event_time = time.time()
            is_match = (expected_event is None or event == expected_event)

        risk = predictive_engine.observe_event(
            event_type=event,
            source=source,
            is_anomaly=not is_match
        )

        if is_match:
            log.add("INFO", f"{SYMBOL_OK} [{source}] OK: {event} is in line. (risk={risk:.1f})")
            with self.lock:
                if self.expected:
                    self.index = (self.index + 1) % len(self.expected)
            event_bus.publish("line_ok", {"event": event, "expected": expected_event, "source": source, "risk": risk})
            return True
        else:
            log.add("WARNING", f"{SYMBOL_BAD} [{source}] ANOMALY: {event} is NOT in line! Expected {expected_event}. (risk={risk:.1f})")
            event_bus.publish("line_anomaly", {"event": event, "expected": expected_event, "source": source, "risk": risk})
            return False

    def fold_event_into_line(self, event):
        """
        Splice an allowed event directly into the expected sequence
        at the current index. This reshapes the line.
        """
        with self.lock:
            if event in self.expected:
                log.add("INFO", f"{SYMBOL_FOLD} Event {event} already in line, skipping fold.")
                return
            insert_pos = self.index
            self.expected.insert(insert_pos, event)
            log.add("INFO", f"{SYMBOL_FOLD} Folded event {event} into line at position {insert_pos}. New length={len(self.expected)}")
            # Do not advance index here; next expected will be this event
            saved_seq = list(self.expected)

        settings["expected_sequence"] = saved_seq
        save_settings(settings)
        event_bus.publish("line_updated", {"expected_sequence": saved_seq})

    def get_last_event_age(self):
        with self.lock:
            return time.time() - self.last_event_time

# -----------------------------
# FOLD MANAGER (HYBRID ALLOW-FOLDING)
# -----------------------------
class FoldManager:
    """
    Hybrid ALLOW-folding:
    - Auto-fold whitelisted / explicit 'allow'
    - Threshold-fold unknown events (N=5)
    - Manual fold for high-risk anomalies
    - Never fold blacklist
    """
    def __init__(self, engine: LineComputer, unknown_threshold=5):
        self.engine = engine
        self.unknown_threshold = unknown_threshold
        self.lock = threading.Lock()
        self.counts = {}  # key -> count
        self.last_anomaly = None  # (event, source, risk)

        event_bus.subscribe("line_anomaly", self._on_line_anomaly)

    def _make_key(self, event, source):
        return f"{event}|{source}"

    def _on_line_anomaly(self, event_type, data):
        if not data:
            return
        event = data.get("event")
        source = data.get("source")
        risk = data.get("risk", 0.0)
        with self.lock:
            self.last_anomaly = (event, source, risk)

    def register_anomaly_for_threshold(self, event, source, risk, is_whitelisted, is_blacklisted):
        """
        Called by policy/system when an anomaly is seen that might be foldable.
        """
        key = self._make_key(event, source)

        # Never fold blacklist
        if is_blacklisted:
            return

        # High risk => manual only, do not auto/threshold fold
        if risk >= predictive_engine.risk_threshold_strict:
            return

        # Whitelisted: auto-fold
        if is_whitelisted:
            log.add("INFO", f"{SYMBOL_FOLD} Auto-folding whitelisted event {event} from {source}.")
            self.engine.fold_event_into_line(event)
            return

        # Unknown: threshold folding
        with self.lock:
            self.counts[key] = self.counts.get(key, 0) + 1
            c = self.counts[key]

        if c >= self.unknown_threshold:
            log.add("INFO", f"{SYMBOL_FOLD} Threshold reached for event {event} from {source} (count={c}), folding into line.")
            self.engine.fold_event_into_line(event)
        else:
            log.add("INFO", f"{SYMBOL_FOLD} Counting anomaly {event} from {source}: {c}/{self.unknown_threshold} before fold.")

    def manual_fold_last(self):
        """
        Called from GUI when operator clicks "Fold last anomaly into line".
        """
        with self.lock:
            la = self.last_anomaly
        if not la:
            log.add("INFO", f"{SYMBOL_FOLD} No last anomaly to fold.")
            return
        event, source, risk = la
        log.add("INFO", f"{SYMBOL_FOLD} MANUAL fold requested for last anomaly {event} from {source} (risk={risk:.1f}).")
        self.engine.fold_event_into_line(event)

fold_manager = None  # will be created after engine exists

# -----------------------------
# PROFILING MANAGER
# -----------------------------
class ProfileManager:
    def __init__(self):
        self.recording = False
        self.sequence = []
        self.lock = threading.Lock()
        self.start_time = None

        event_bus.subscribe("sys_raw_event", self._on_sys_raw_event)

    def _on_sys_raw_event(self, event_type, data):
        if not self.recording:
            return
        if not data:
            return
        event_name = data.get("event")
        if not event_name:
            return
        with self.lock:
            if not self.sequence or self.sequence[-1] != event_name:
                self.sequence.append(event_name)

    def start(self):
        with self.lock:
            self.sequence = []
            self.recording = True
            self.start_time = time.time()
        log.add("INFO", f"{SYMBOL_PROFILE} Profiling started. Learning normal system line.")

    def stop(self):
        with self.lock:
            self.recording = False
            start = self.start_time
            self.start_time = None
        if start:
            duration = time.time() - start
            log.add("INFO", f"{SYMBOL_PROFILE} Profiling stopped. Collected {len(self.sequence)} steps over {duration:.1f}s.")
        else:
            log.add("INFO", f"{SYMBOL_PROFILE} Profiling stopped.")

    def lock_profile_into_engine(self, engine: LineComputer):
        with self.lock:
            learned = list(self.sequence)
            start = self.start_time
        if not learned:
            log.add("WARNING", f"{SYMBOL_PROFILE} No profile sequence to lock. Skipping.")
            return

        engine.set_expected_sequence(learned)

        metadata = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "host": socket.gethostname(),
            "duration_seconds": None,
            "notes": "Baseline profile locked from system events."
        }
        if start:
            metadata["duration_seconds"] = time.time() - start

        settings["expected_sequence"] = learned
        settings["profile_sequence"] = learned
        settings["profile_metadata"] = metadata
        save_settings(settings)

        log.add("INFO", f"{SYMBOL_PROFILE} Profile locked. Engine now using learned system line.")
        log.add("INFO", f"{SYMBOL_PROFILE} Profile metadata: host={metadata['host']} created_at={metadata['created_at']}")

    def get_sequence(self):
        with self.lock:
            return list(self.sequence)

    def get_metadata(self):
        return settings.get("profile_metadata", {})

profile_manager = ProfileManager()

# -----------------------------
# SWARM NODES + DASHBOARD
# -----------------------------
class SwarmNode:
    def __init__(self, node_id, sequence):
        self.node_id = node_id
        self.sequence = list(sequence)
        self.lock = threading.Lock()
        self.shared_risk = 0.0

    def sync(self, other_node):
        with self.lock, other_node.lock:
            merged = list(dict.fromkeys(self.sequence + other_node.sequence))
            self.sequence = merged
            other_node.sequence = merged
            avg_risk = (self.shared_risk + other_node.shared_risk) / 2.0
            self.shared_risk = avg_risk
            other_node.shared_risk = avg_risk

        msg = f"{SYMBOL_SYNC} Node {self.node_id} synced with Node {other_node.node_id} (shared_risk={self.shared_risk:.1f})"
        log.add("INFO", msg)
        event_bus.publish("swarm_sync", msg)

class SwarmManager:
    def __init__(self, node_count, base_sequence):
        self.nodes = [SwarmNode(i + 1, base_sequence) for i in range(node_count)]
        self.running = False
        self.thread = None

        event_bus.subscribe("line_updated", self._on_line_updated)

    def _on_line_updated(self, event_type, data):
        if not data:
            return
        new_seq = data.get("expected_sequence") or []
        for node in self.nodes:
            with node.lock:
                node.sequence = list(new_seq)

    def start(self, interval=2.0):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(interval,), daemon=True)
        self.thread.start()
        log.add("INFO", "Swarm manager started.")

    def stop(self):
        self.running = False
        log.add("INFO", "Swarm manager stopped.")

    def _run(self, interval):
        while self.running:
            time.sleep(interval)
            if len(self.nodes) < 2:
                continue
            import random
            a, b = random.sample(self.nodes, 2)
            a.sync(b)

            current_risk = predictive_engine.get_risk()
            for n in self.nodes:
                with n.lock:
                    n.shared_risk = (n.shared_risk * 0.8) + (current_risk * 0.2)

    def get_status_lines(self):
        lines = []
        for node in self.nodes:
            with node.lock:
                seq_str = ",".join(node.sequence)
                risk = node.shared_risk
            lines.append(f"Node {node.node_id}: [{seq_str}] shared_risk={risk:.1f}")
        return lines

# -----------------------------
# WATCHDOG (DAEMONIZED THREAD)
# -----------------------------
class Watchdog:
    def __init__(self, engine: LineComputer, timeout=5.0, check_interval=1.0):
        self.engine = engine
        self.timeout = timeout
        self.check_interval = check_interval
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        log.add("INFO", f"{SYMBOL_WATCHDOG} Watchdog started (timeout={self.timeout}s).")

    def stop(self):
        self.running = False
        log.add("INFO", f"{SYMBOL_WATCHDOG} Watchdog stopped.")

    def _run(self):
        while self.running:
            time.sleep(self.check_interval)
            age = self.engine.get_last_event_age()
            if age > self.timeout:
                msg = f"{SYMBOL_WATCHDOG} Watchdog: no events for {age:.1f}s – potential stall."
                log.add("WARNING", msg)
                event_bus.publish("watchdog_alert", msg)

# -----------------------------
# REAL-TIME EVENT GENERATOR (SIM)
# -----------------------------
class EventGenerator:
    def __init__(self, engine: LineComputer, interval=0.5, anomaly_rate=0.2):
        self.engine = engine
        self.interval = interval
        self.anomaly_rate = anomaly_rate
        self.running = False
        self.thread = None
        self.valid_events = ["LEFT", "RIGHT"]
        self.anomaly_events = ["ROCK", "BRANCH", "GLITCH"]

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        log.add("INFO", "Event generator started.")

    def stop(self):
        self.running = False
        log.add("INFO", "Event generator stopped.")

    def _run(self):
        import random
        while self.running:
            time.sleep(self.interval)
            if random.random() < self.anomaly_rate:
                event = random.choice(self.anomaly_events)
                source = "sim-anomaly"
            else:
                event = random.choice(self.valid_events)
                source = "sim"
            self.engine.process(event, source=source)

# -----------------------------
# PER-PROCESS POLICY ENGINE
# -----------------------------
class ProcessPolicyEngine:
    def __init__(self, engine: LineComputer, policy_map):
        self.engine = engine
        self.policy_map = {k.upper(): v for k, v in (policy_map or {}).items()}

    def decide_action(self, name: str, default_action: str):
        key = (name or "").upper()
        return self.policy_map.get(key, default_action)

    def apply_action(self, pid: str, name: str, action: str, event_type: str, source: str,
                     is_whitelisted: bool, is_blacklisted: bool):
        match = self.engine.process(event_type, source=source)
        risk = predictive_engine.get_risk()

        # Hybrid folding - feed threshold manager (unknown + WL, non-blacklist)
        if fold_manager is not None:
            fold_manager.register_anomaly_for_threshold(
                event=event_type,
                source=source,
                risk=risk,
                is_whitelisted=is_whitelisted or (action == "allow"),
                is_blacklisted=is_blacklisted
            )

        # Predictive auto-strict behavior
        if risk >= predictive_engine.risk_threshold_strict and not self.engine.is_strict_mode():
            log.add("WARNING", f"{SYMBOL_PRED} Risk {risk:.1f} >= strict threshold, enabling strict mode.")
            self.engine.set_strict_mode(True)
        elif risk < predictive_engine.risk_threshold_warn and self.engine.is_strict_mode():
            log.add("INFO", f"{SYMBOL_PRED} Risk {risk:.1f} below warn threshold, strict mode can be relaxed (manual).")

        # Interpret "allow" as "log + fold candidate", not kill/isolate
        if action == "allow":
            action_effective = "log"
        else:
            action_effective = action

        if not self.engine.is_strict_mode():
            if action_effective == "alert":
                log.add("WARNING", f"{SYMBOL_STRICT} Policy ALERT on process {name} (pid={pid}) event={event_type}, risk={risk:.1f}")
            elif action_effective == "kill":
                log.add("WARNING", f"{SYMBOL_STRICT} Policy would KILL {name} (pid={pid}) [strict off, no kill], risk={risk:.1f}")
            threat_matrix.record(event_type, None if match else "LINE_MISMATCH",
                                 source=source, action=action_effective, score=risk)
            return

        if action_effective == "ignore":
            return

        if action_effective == "log":
            threat_matrix.record(event_type, None if match else "LINE_MISMATCH",
                                 source=source, action=action_effective, score=risk)
            return

        if action_effective == "alert":
            log.add("WARNING", f"{SYMBOL_STRICT} STRICT ALERT on process {name} (pid={pid}) event={event_type}, risk={risk:.1f}")
            threat_matrix.record(event_type, None if match else "LINE_MISMATCH",
                                 source=source, action=action_effective, score=risk)
            return

        if action_effective == "kill":
            killed = False
            if psutil:
                try:
                    pid_int = int(pid)
                    p = psutil.Process(pid_int)
                    p.terminate()
                    killed = True
                    log.add("WARNING", f"{SYMBOL_STRICT} STRICT KILL executed on {name} (pid={pid}) risk={risk:.1f}")
                except Exception as e:
                    log.add("ERROR", f"{SYMBOL_STRICT} Failed to kill {name} (pid={pid}): {e}")
            else:
                log.add("WARNING", f"{SYMBOL_STRICT} STRICT KILL requested for {name} (pid={pid}), but psutil not available. risk={risk:.1f}")
            threat_matrix.record(event_type, None if match else "LINE_MISMATCH",
                                 source=source,
                                 action=("kill-ok" if killed else "kill-failed"),
                                 score=risk)

# -----------------------------
# SYSTEM EVENT COLLECTOR
# -----------------------------
class SystemEventCollector:
    def __init__(self, engine: LineComputer, policy_engine: ProcessPolicyEngine,
                 poll_interval=2.0,
                 whitelist=None, blacklist=None):
        self.engine = engine
        self.policy_engine = policy_engine
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None

        self.known_procs = set()
        self.cpu_baseline = None

        self.whitelist = set((whitelist or []))
        self.blacklist = set((blacklist or []))

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        log.add("INFO", f"{SYMBOL_SYS} System collector started (interval={self.poll_interval}s).")

    def stop(self):
        self.running = False
        log.add("INFO", f"{SYMBOL_SYS} System collector stopped.")

    def _run(self):
        self.known_procs = self._get_current_proc_keys()
        self.cpu_baseline = self._get_cpu_load()

        while self.running:
            time.sleep(self.poll_interval)
            self._check_processes()
            self._check_cpu()

    def _get_current_proc_keys(self):
        keys = set()
        if psutil:
            for p in psutil.process_iter(["pid", "name"]):
                pid = p.info.get("pid")
                name = p.info.get("name") or "UNKNOWN"
                keys.add(f"{pid}:{name}")
        else:
            try:
                if os.name == "nt":
                    out = subprocess.check_output(["tasklist"])
                    for line in out.splitlines()[3:]:
                        parts = line.decode(errors="ignore").split()
                        if len(parts) >= 2:
                            name, pid = parts[0], parts[1]
                            keys.add(f"{pid}:{name}")
                else:
                    out = subprocess.check_output(["ps", "-eo", "pid,comm"])
                    for line in out.splitlines()[1:]:
                        parts = line.decode(errors="ignore").split(None, 1)
                        if len(parts) == 2:
                            pid, name = parts
                            keys.add(f"{pid}:{name}")
            except Exception:
                pass
        return keys

    def _get_cpu_load(self):
        if psutil:
            return psutil.cpu_percent(interval=None)
        else:
            return None

    def _check_processes(self):
        current = self._get_current_proc_keys()
        new_procs = current - self.known_procs
        dead_procs = self.known_procs - current
        self.known_procs = current

        for key in new_procs:
            pid, name = self._split_proc_key(key)
            base_name_upper = (name or "").upper()
            wl_match = any(base_name_upper == n.upper() for n in self.whitelist)
            bl_match = any(base_name_upper == n.upper() for n in self.blacklist)

            if bl_match:
                event_type = "PROC_BLACKLISTED"
                default_action = "kill"
                source = f"sys-proc-bl:{name}"
            elif wl_match:
                event_type = "PROC_WHITELISTED"
                default_action = "allow"  # auto-fold path
                source = f"sys-proc-wl:{name}"
            else:
                event_type = "PROC_NEW"
                default_action = "alert" if self.engine.is_strict_mode() else "log"
                source = f"sys-proc:{name}"

            raw_payload = {"event": event_type, "name": name, "pid": pid, "source": source}
            event_bus.publish("sys_raw_event", raw_payload)

            action = self.policy_engine.decide_action(name, default_action)
            self.policy_engine.apply_action(pid, name, action, event_type, source,
                                            is_whitelisted=wl_match,
                                            is_blacklisted=bl_match)

        if len(dead_procs) > 0 and len(dead_procs) > 10:
            event_type = "PROC_STORM"
            raw_payload = {"event": event_type, "count": len(dead_procs), "source": "sys-proc-storm"}
            event_bus.publish("sys_raw_event", raw_payload)
            self.engine.process(event_type, source="sys-proc-storm")

    def _check_cpu(self):
        current = self._get_cpu_load()
        if current is None:
            return
        if self.cpu_baseline is None:
            self.cpu_baseline = current
            return

        if current > self.cpu_baseline + 50:
            event_type = "CPU_SPIKE"
            raw_payload = {"event": event_type, "value": current, "source": "sys-cpu"}
            event_bus.publish("sys_raw_event", raw_payload)
            self.engine.process(event_type, source="sys-cpu")
        elif current < self.cpu_baseline - 30:
            event_type = "CPU_DROP"
            raw_payload = {"event": event_type, "value": current, "source": "sys-cpu"}
            event_bus.publish("sys_raw_event", raw_payload)
            self.engine.process(event_type, source="sys-cpu")

    def _split_proc_key(self, key):
        try:
            pid, name = key.split(":", 1)
            return pid, name
        except ValueError:
            return "?", key

# -----------------------------
# GUI COCKPIT
# -----------------------------
class LineGUI:
    def __init__(self, root, engine: LineComputer, swarm: SwarmManager,
                 watchdog: Watchdog, generator: EventGenerator,
                 sys_collector: SystemEventCollector, profiler: ProfileManager,
                 fold_mgr: FoldManager):
        self.root = root
        self.engine = engine
        self.swarm = swarm
        self.watchdog = watchdog
        self.generator = generator
        self.sys_collector = sys_collector
        self.profiler = profiler
        self.fold_mgr = fold_mgr

        self.root.title("Line Computing Cockpit")
        self.root.geometry("1200x760")

        self.ui_queue = queue.Queue()
        self.current_risk = 0.0

        self._build_layout()
        self._wire_events()
        self._start_polling_ui_queue()

    def _build_layout(self):
        top_frame = tkinter.Frame(self.root)
        top_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        btn_frame = tkinter.Frame(top_frame)
        btn_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        profile_frame = tkinter.Frame(top_frame)
        profile_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        strict_frame = tkinter.Frame(top_frame)
        strict_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        fold_frame = tkinter.Frame(top_frame)
        fold_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        meta_frame = tkinter.Frame(top_frame)
        meta_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        risk_frame = tkinter.Frame(top_frame)
        risk_frame.pack(side=tkinter.LEFT, padx=5, pady=5)

        status_frame = tkinter.Frame(top_frame)
        status_frame.pack(side=tkinter.RIGHT, padx=5, pady=5)

        # System control
        self.btn_start = tkinter.Button(btn_frame, text="Start System", command=self.start_system)
        self.btn_stop = tkinter.Button(btn_frame, text="Stop System", command=self.stop_system)
        self.btn_start.pack(side=tkinter.LEFT, padx=5)
        self.btn_stop.pack(side=tkinter.LEFT, padx=5)

        # Profiling control
        self.btn_profile_start = tkinter.Button(profile_frame, text="Start Profiling", command=self.start_profiling)
        self.btn_profile_stop = tkinter.Button(profile_frame, text="Stop Profiling", command=self.stop_profiling)
        self.btn_profile_lock = tkinter.Button(profile_frame, text="Lock Profile", command=self.lock_profile)
        self.btn_profile_start.pack(side=tkinter.LEFT, padx=3)
        self.btn_profile_stop.pack(side=tkinter.LEFT, padx=3)
        self.btn_profile_lock.pack(side=tkinter.LEFT, padx=3)

        # Strict mode
        self.strict_var = tkinter.BooleanVar(value=self.engine.is_strict_mode())
        self.chk_strict = tkinter.Checkbutton(strict_frame, text="Strict Mode", variable=self.strict_var,
                                              command=self.toggle_strict_mode)
        self.chk_strict.pack(side=tkinter.LEFT, padx=5)

        # Manual fold button
        self.btn_manual_fold = tkinter.Button(fold_frame, text="Fold Last Anomaly", command=self.manual_fold_last)
        self.btn_manual_fold.pack(side=tkinter.LEFT, padx=5)

        # Profile metadata display
        self.label_profile_meta = tkinter.Label(meta_frame, text="Profile: none", fg="blue")
        self.label_profile_meta.pack(side=tkinter.LEFT, padx=5)
        self._update_profile_metadata_label()

        # Risk display
        self.label_risk = tkinter.Label(risk_frame, text="Risk: 0.0 (NORMAL)", fg="green")
        self.label_risk.pack(side=tkinter.LEFT, padx=5)

        # Status
        self.label_status = tkinter.Label(status_frame, text="Status: IDLE", fg="gray")
        self.label_status.pack(side=tkinter.RIGHT)

        # Main area
        main_frame = tkinter.Frame(self.root)
        main_frame.pack(fill=tkinter.BOTH, expand=True)

        log_frame = tkinter.LabelFrame(main_frame, text="Live Log")
        log_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=5, pady=5)

        self.txt_log = scrolledtext.ScrolledText(log_frame, wrap=tkinter.WORD, height=20)
        self.txt_log.pack(fill=tkinter.BOTH, expand=True)

        right_frame = tkinter.Frame(main_frame)
        right_frame.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True)

        threat_frame = tkinter.LabelFrame(right_frame, text="Threat Matrix")
        threat_frame.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)

        self.list_threats = tkinter.Listbox(threat_frame, height=10)
        self.list_threats.pack(fill=tkinter.BOTH, expand=True)

        swarm_frame = tkinter.LabelFrame(right_frame, text="Swarm Dashboard")
        swarm_frame.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)

        self.list_swarm = tkinter.Listbox(swarm_frame, height=10)
        self.list_swarm.pack(fill=tkinter.BOTH, expand=True)

    def _wire_events(self):
        event_bus.subscribe("log", self._on_log_event)
        event_bus.subscribe("threat", self._on_threat_event)
        event_bus.subscribe("swarm_sync", self._on_swarm_event)
        event_bus.subscribe("watchdog_alert", self._on_watchdog_event)
        event_bus.subscribe("predictive_risk", self._on_risk_event)

        self.root.after(1000, self._refresh_swarm_status)

    def _on_log_event(self, event_type, data):
        self.ui_queue.put(("log", data))

    def _on_threat_event(self, event_type, data):
        self.ui_queue.put(("threat", data))

    def _on_swarm_event(self, event_type, data):
        self.ui_queue.put(("swarm_log", data))

    def _on_watchdog_event(self, event_type, data):
        self.ui_queue.put(("log", data))

    def _on_risk_event(self, event_type, data):
        if not data:
            return
        self.ui_queue.put(("risk", data))

    def _start_polling_ui_queue(self):
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "log":
                    self._append_log(payload)
                elif kind == "threat":
                    self._add_threat(payload)
                elif kind == "swarm_log":
                    self._append_log(payload)
                elif kind == "risk":
                    self._update_risk(payload.get("risk", 0.0))
        except queue.Empty:
            pass
        self.root.after(100, self._start_polling_ui_queue)

    def _append_log(self, line):
        self.txt_log.insert(tkinter.END, line + "\n")
        self.txt_log.see(tkinter.END)

    def _add_threat(self, line):
        self.list_threats.insert(tkinter.END, line)
        self.list_threats.see(tkinter.END)

    def _refresh_swarm_status(self):
        self.list_swarm.delete(0, tkinter.END)
        for line in self.swarm.get_status_lines():
            self.list_swarm.insert(tkinter.END, line)
        self.root.after(1000, self._refresh_swarm_status)

    def _update_profile_metadata_label(self):
        meta = profile_manager.get_metadata()
        if not meta:
            txt = "Profile: none"
        else:
            created = meta.get("created_at", "?")
            host = meta.get("host", "?")
            txt = f"Profile: {created} @ {host}"
        self.label_profile_meta.config(text=txt)

    def _update_risk(self, risk):
        self.current_risk = risk
        level = predictive_engine.classify_risk_level()
        if level == "HIGH":
            color = "red"
        elif level == "WARN":
            color = "orange"
        else:
            color = "green"
        self.label_risk.config(text=f"Risk: {risk:.1f} ({level})", fg=color)

    # Control buttons
    def start_system(self):
        self.generator.start()
        self.watchdog.start()
        self.swarm.start(interval=3.0)
        self.sys_collector.start()
        self.label_status.config(text="Status: RUNNING", fg="green")

    def stop_system(self):
        self.generator.stop()
        self.watchdog.stop()
        self.swarm.stop()
        self.sys_collector.stop()
        self.label_status.config(text="Status: STOPPED", fg="red")

    # Profiling controls
    def start_profiling(self):
        profile_manager.start()
        self._append_log(f"{SYMBOL_PROFILE} Profiling requested from GUI.")

    def stop_profiling(self):
        profile_manager.stop()
        seq_len = len(profile_manager.get_sequence())
        self._append_log(f"{SYMBOL_PROFILE} Profiling stopped. Steps learned: {seq_len}")

    def lock_profile(self):
        profile_manager.stop()
        profile_manager.lock_profile_into_engine(self.engine)
        self._update_profile_metadata_label()
        self._append_log(f"{SYMBOL_PROFILE} Profile locked into engine as new expected sequence.")

    # Strict mode
    def toggle_strict_mode(self):
        enabled = self.strict_var.get()
        self.engine.set_strict_mode(enabled)

    # Manual fold
    def manual_fold_last(self):
        if self.fold_mgr:
            self.fold_mgr.manual_fold_last()

# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
def main():
    global fold_manager

    engine = LineComputer(
        settings.get("expected_sequence", ["LEFT", "RIGHT"]),
        strict_mode=settings.get("strict_mode", False)
    )

    fold_manager = FoldManager(
        engine,
        unknown_threshold=settings.get("folding", {}).get("unknown_threshold", 5)
    )

    swarm = SwarmManager(settings.get("swarm_nodes", 3), engine.get_expected_sequence())

    watchdog = Watchdog(
        engine,
        timeout=settings.get("watchdog_timeout", 5.0),
        check_interval=1.0
    )

    generator = EventGenerator(
        engine,
        interval=settings.get("event_interval", 0.5),
        anomaly_rate=0.3
    )

    policy_engine = ProcessPolicyEngine(
        engine,
        settings.get("process_policies", {})
    )

    sys_collector = SystemEventCollector(
        engine,
        policy_engine=policy_engine,
        poll_interval=settings.get("system_poll_interval", 2.0),
        whitelist=settings.get("process_whitelist", []),
        blacklist=settings.get("process_blacklist", [])
    )

    root = tkinter.Tk()
    gui = LineGUI(root, engine, swarm, watchdog, generator, sys_collector, profile_manager, fold_manager)

    try:
        root.mainloop()
    finally:
        generator.stop()
        watchdog.stop()
        swarm.stop()
        sys_collector.stop()
        save_settings(settings)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

