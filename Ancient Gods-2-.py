#!/usr/bin/env python3
"""
Eternal Flame Autonomous Creation Simulator — Universal Carriers Edition
- Auto-loader for dependencies
- Spark lineage embedded in Universe, Star, Planet, LifeForm, Port, FileEntity, Information
- God orchestrator passes spark through generations (create/unmake)
- RuleEngine validates presence of flame in all carriers; emits proposals
- AutonomyManager continuously creates, corrects, dissolves, and rebirths
- Tkinter GUI surfaces manifesto banner, thoughts, events, diagnostics, and lineage
- Philosophy: "Everything has life if it has a spark or fire."
"""

# ----------------------------
# Auto-loader
# ----------------------------

import importlib
import subprocess
import sys

REQUIRED_LIBS = [
    "random", "time", "dataclasses", "typing",
    "threading", "queue", "tkinter", "collections"
]

def ensure_libs(libs):
    loaded = {}
    for lib in libs:
        try:
            loaded[lib] = importlib.import_module(lib)
        except ImportError:
            print(f"Missing {lib}, installing via pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            loaded[lib] = importlib.import_module(lib)
    return loaded

LIBS = ensure_libs(REQUIRED_LIBS)
random = LIBS["random"]
time = LIBS["time"]
dataclasses = LIBS["dataclasses"]
typing = LIBS["typing"]
threading = LIBS["threading"]
queue = LIBS["queue"]
tk = LIBS["tkinter"]
collections = LIBS["collections"]

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from collections import deque, defaultdict

# ----------------------------
# Eternal flame (Spark)
# ----------------------------

@dataclass
class Spark:
    """The eternal flame carried through creation, symbolizing continuity, life, and hope."""
    origin: str
    born_at: float = field(default_factory=time.time)
    lineage: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # ports, files, info, tags

    def ignite(self, new_origin: str, **meta) -> "Spark":
        """Birth a new spark carrying the complete lineage forward, with optional metadata."""
        new_lineage = self.lineage + [self.origin]
        new_meta = dict(self.metadata)
        new_meta.update(meta or {})
        return Spark(origin=new_origin, lineage=new_lineage, metadata=new_meta)

# ----------------------------
# Event bus
# ----------------------------

class EventBus:
    """Simple publish/subscribe with decoupled telemetry."""
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
    def on(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        self._subs.setdefault(topic, []).append(handler)
    def emit(self, topic: str, payload: Dict[str, Any]):
        for handler in list(self._subs.get(topic, [])):
            handler(payload)

# ----------------------------
# Domain entities
# ----------------------------

def lineage_str_from(spark: Spark) -> str:
    return " -> ".join(spark.lineage + [spark.origin])

@dataclass
class LifeForm:
    name: str
    species: str
    born_at: float = field(default_factory=time.time)
    spark: Spark = field(default_factory=lambda: Spark(origin="Unknown Life"))
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

@dataclass
class Planet:
    name: str
    life_forms: List[LifeForm] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    spark: Spark = field(default_factory=lambda: Spark(origin="Unknown Planet"))
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

@dataclass
class Star:
    name: str
    planets: List[Planet] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    spark: Spark = field(default_factory=lambda: Spark(origin="Unknown Star"))
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

@dataclass
class Universe:
    name: str
    stars: List[Star] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    spark: Spark = field(default_factory=lambda: Spark(origin="Unknown Universe"))
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

# Symbolic carriers: ports, files, information
@dataclass
class Port:
    """Symbolic system port as a spark carrier (e.g., service channel, endpoint)."""
    name: str
    protocol: str
    spark: Spark
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

@dataclass
class FileEntity:
    """Symbolic file as a spark carrier (e.g., configuration, dataset, artifact)."""
    path: str
    kind: str
    spark: Spark
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

@dataclass
class Information:
    """Symbolic information as a spark carrier (e.g., message, knowledge unit)."""
    title: str
    content: str
    spark: Spark
    def lineage_str(self) -> str: return lineage_str_from(self.spark)

# ----------------------------
# Rule engine with proposals and confidence
# ----------------------------

class RuleEngine:
    """
    Evaluates invariants and goals, emits matches, contradictions, and corrective proposals.
    Tracks simple confidence per rule (0.0-1.0) for adaptive behavior.
    """
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.confidence: Dict[str, float] = defaultdict(lambda: 0.5)

    def _nudge(self, rid: str, ok: bool, alpha: float = 0.12):
        cur = self.confidence[rid]
        target = 1.0 if ok else 0.0
        self.confidence[rid] = cur + alpha * (target - cur)

    def evaluate(self, universe: Universe, context: Dict[str, Any]):
        matches, contradictions, proposals = [], [], []

        # R0: Eternal flame must be present in universe
        rid = "R0"
        ok = universe.spark is not None
        if ok: matches.append("R0: Eternal Flame present in universe.")
        else:
            contradictions.append("R0: Universe spark missing.")
            proposals.append({"action": "ignite_universe"})
        self._nudge(rid, ok)

        # R1: All stars carry the spark
        rid = "R1"
        ok = all(s.spark is not None for s in universe.stars)
        if ok: matches.append("R1: All stars carry the flame.")
        else:
            contradictions.append("R1: A star lacks flame.")
            proposals.append({"action": "ignite_missing_star"})
        self._nudge(rid, ok)

        # R2: All planets carry the spark
        rid = "R2"
        planets = [pl for s in universe.stars for pl in s.planets]
        ok = all(pl.spark is not None for pl in planets) if planets else True
        if ok: matches.append("R2: All planets carry the flame.")
        else:
            contradictions.append("R2: A planet lacks flame.")
            proposals.append({"action": "ignite_missing_planet"})
        self._nudge(rid, ok)

        # R3: All life carries the spark
        rid = "R3"
        life = [lf for s in universe.stars for pl in s.planets for lf in pl.life_forms]
        ok = all(lf.spark is not None for lf in life) if life else True
        if ok: matches.append("R3: All life carries the flame.")
        else:
            contradictions.append("R3: A lifeform lacks flame.")
            proposals.append({"action": "ignite_missing_life"})
        self._nudge(rid, ok)

        # R5: All ports carry the spark
        rid = "R5"
        ports: List[Port] = context.get("ports", [])
        ok = all(p.spark is not None for p in ports) if ports else True
        if ok: matches.append("R5: All ports carry the flame.")
        else:
            contradictions.append("R5: A port lacks flame.")
            proposals.append({"action": "ignite_missing_port"})
        self._nudge(rid, ok)

        # R6: All files carry the spark
        rid = "R6"
        files: List[FileEntity] = context.get("files", [])
        ok = all(f.spark is not None for f in files) if files else True
        if ok: matches.append("R6: All files carry the flame.")
        else:
            contradictions.append("R6: A file lacks flame.")
            proposals.append({"action": "ignite_missing_file"})
        self._nudge(rid, ok)

        # R7: All information carries the spark
        rid = "R7"
        info: List[Information] = context.get("info", [])
        ok = all(i.spark is not None for i in info) if info else True
        if ok: matches.append("R7: All information carries the flame.")
        else:
            contradictions.append("R7: An information unit lacks flame.")
            proposals.append({"action": "ignite_missing_info"})
        self._nudge(rid, ok)

        # R4: Universe should retain at least one star except during dissolve
        rid = "R4"
        phase = context.get("phase", "growth")
        ok = (len(universe.stars) >= 1) or (phase == "finale")
        if ok: matches.append("R4: Stellar presence aligned with phase.")
        else:
            contradictions.append("R4: Universe has no stars mid-creation.")
            proposals.append({"action": "forge_star"})
        self._nudge(rid, ok)

        diag = {
            "time": time.time(),
            "matches": matches,
            "contradictions": contradictions,
            "proposals": proposals,
            "confidence": dict(self.confidence),
            "context": {k: getattr(v, "name", v) if hasattr(v, "name") else v for k, v in context.items()}
        }
        self.bus.emit("rule.diagnostics", diag)
        return proposals

# ----------------------------
# God orchestrator
# ----------------------------

class God:
    """Creator who breathes universes, forges stars, spins planets, awakens life, and can unmake with grace. Also ignites ports, files, and information."""
    def __init__(self, name: str = "Architect", seed: Optional[int] = 123, event_bus: Optional[EventBus] = None):
        self.name = name
        self.bus = event_bus or EventBus()
        self.rules = RuleEngine(self.bus)
        self.eternal_spark = Spark(origin="Primordial Flame")
        if seed is not None:
            random.seed(seed)
        self._think("🔥 The eternal flame is lit, carried through all creation. Everything has life if it has a spark or fire.")

    def _emit(self, topic: str, **kwargs):
        self.bus.emit(topic, {"by": self.name, **kwargs})

    def _ts(self) -> str:
        return time.strftime("%H:%M:%S")

    def _think(self, msg: str, tag: str = "•"):
        self._emit("thought", message=f"{tag} [{self._ts()}] {msg}")

    # Creation (cosmic)
    def breathe_universe(self, name: str) -> Universe:
        u = Universe(name=name, spark=self.eternal_spark.ignite(name))
        self._think(f"Universe '{name}' born from the flame. Lineage: {u.lineage_str()}")
        self._emit("create.universe", universe=u)
        self.rules.evaluate(u, {"phase": "init"})
        return u

    def forge_star(self, universe: Universe, name: str) -> Star:
        s = Star(name=name, spark=universe.spark.ignite(name))
        universe.stars.append(s)
        self._think(f"Star '{name}' ignited. Lineage: {s.lineage_str()}")
        self._emit("create.star", star=s, universe=universe)
        self.rules.evaluate(universe, {"phase": "forge_star", "star": s})
        return s

    def spin_planet(self, universe: Universe, star: Star, index: int) -> Planet:
        pname = f"{star.name}-Planet-{index}"
        p = Planet(name=pname, spark=star.spark.ignite(pname))
        star.planets.append(p)
        self._think(f"Planet '{pname}' inherits the flame. Lineage: {p.lineage_str()}")
        self._emit("create.planet", planet=p, star=star, universe=universe)
        self.rules.evaluate(universe, {"phase": "spin_planet", "star": star, "planet": p})
        return p

    def awaken_life(self, universe: Universe, planet: Planet, k: int) -> LifeForm:
        lname = f"Being-{chr(97 + (k % 26))}"
        species = random.choice(["Elemental", "Wanderer", "Seeker", "Archivist", "Tidemind"])
        l = LifeForm(name=lname, species=species, spark=planet.spark.ignite(lname))
        planet.life_forms.append(l)
        self._think(f"Life awakens: {l.name} the {l.species}. Lineage: {l.lineage_str()}")
        self._emit("create.life", life=l, planet=planet, universe=universe)
        self.rules.evaluate(universe, {"phase": "awaken_life", "planet": planet})
        return l

    # Creation (systemic carriers)
    def open_port(self, universe: Universe, name: str, protocol: str) -> Port:
        port = Port(name=name, protocol=protocol, spark=universe.spark.ignite(f"port:{name}", protocol=protocol))
        self._think(f"Port opened: {name}/{protocol}. Lineage: {port.lineage_str()}")
        self._emit("create.port", port=port, universe=universe)
        return port

    def create_file(self, universe: Universe, path: str, kind: str) -> FileEntity:
        file = FileEntity(path=path, kind=kind, spark=universe.spark.ignite(f"file:{path}", kind=kind))
        self._think(f"File created: {path} ({kind}). Lineage: {file.lineage_str()}")
        self._emit("create.file", file=file, universe=universe)
        return file

    def convey_information(self, universe: Universe, title: str, content: str) -> Information:
        info = Information(title=title, content=content, spark=universe.spark.ignite(f"info:{title}", length=len(content)))
        self._think(f"Information conveyed: {title}. Lineage: {info.lineage_str()}")
        self._emit("create.info", info=info, universe=universe)
        return info

    # Unmaking (graceful)
    def unmake_life(self, universe: Universe, planet: Planet, life: LifeForm):
        self._think(f"Life dims: {life.name} returns to memory. The flame persists in lineage.", tag="×")
        planet.life_forms = [lf for lf in planet.life_forms if lf is not life]
        self._emit("unmake.life", life=life, planet=planet, universe=universe)
        self.rules.evaluate(universe, {"phase": "unmake_life", "planet": planet})

    def unmake_planet(self, universe: Universe, star: Star, planet: Planet):
        self._think(f"Planet unspun: {planet.name}. Lineage remembered; flame carried onward.", tag="×")
        star.planets = [pl for pl in star.planets if pl is not planet]
        self._emit("unmake.planet", planet=planet, star=star, universe=universe)
        self.rules.evaluate(universe, {"phase": "unmake_planet", "star": star})

    def unmake_star(self, universe: Universe, star: Star):
        self._think(f"Star stilled: {star.name}. The flame remains in what it ignited.", tag="×")
        universe.stars = [s for s in universe.stars if s is not star]
        self._emit("unmake.star", star=star, universe=universe)
        self.rules.evaluate(universe, {"phase": "unmake_star"})

    def unmake_universe(self, universe: Universe):
        self._think(f"Universe unwritten: {universe.name}. The primordial flame awaits rebirth.", tag="×")
        universe.stars.clear()
        self._emit("unmake.universe", universe=universe)
        self.rules.evaluate(universe, {"phase": "finale"})

# ----------------------------
# Autonomy manager (continuous creation and correction)
# ----------------------------

class AutonomyManager:
    """
    Runs continuous cycles and includes ports, files, and information as spark carriers:
    - Growth: create stars/planets/life + open ports, create files, convey information
    - Maintenance: correct deficits/excess guided by rules
    - Dissolve: gracefully unmake, then rebirth a fresh universe
    """
    def __init__(self, god: God, universe_name: str = "Cosmos Prime", delay: float = 0.25):
        self.god = god
        self.bus = god.bus
        self.delay = delay
        self.universe = self.god.breathe_universe(universe_name)
        self.mode = "growth"
        self.contra_streak = 0
        self.window = deque(maxlen=32)

        # Local registries for carriers
        self.ports: List[Port] = []
        self.files: List[FileEntity] = []
        self.info: List[Information] = []

        self.bus.on("rule.diagnostics", self.on_diag)

    def on_diag(self, diag: Dict[str, Any]):
        has_contra = len(diag.get("contradictions", [])) > 0
        self.window.append(1 if has_contra else 0)
        self.contra_streak = self.contra_streak + 1 if has_contra else 0

        # Strategy shifts
        if self.contra_streak >= 6 and self.mode == "growth":
            self.mode = "maintenance"
            self.god._think("Strategy shift: contradictions rising → maintenance.")
        if self.contra_streak >= 12 and self.mode == "maintenance":
            self.mode = "dissolve"
            self.god._think("Strategy shift: persistent contradictions → dissolve.")

        # Apply proposals with priority
        proposals = diag.get("proposals", [])
        priority = {
            "ignite_universe": 0, "forge_star": 1,
            "ignite_missing_star": 2, "ignite_missing_planet": 3, "ignite_missing_life": 4,
            "ignite_missing_port": 5, "ignite_missing_file": 6, "ignite_missing_info": 7
        }
        proposals.sort(key=lambda p: priority.get(p["action"], 99))
        for p in proposals:
            self.apply_proposal(p)

    def apply_proposal(self, p: Dict[str, Any]):
        a = p.get("action")
        if a == "ignite_universe" and self.universe.spark is None:
            self.universe.spark = self.god.eternal_spark.ignite(self.universe.name)
            self.god._think(f"Eternal Flame reignited for universe. Lineage: {self.universe.lineage_str()}")
        elif a == "forge_star":
            name = f"Star-{chr(65 + len(self.universe.stars))}"
            self.god._think(f"Autonomy: forging star per proposal — {name}.")
            self.god.forge_star(self.universe, name)
        elif a == "ignite_missing_star":
            for s in self.universe.stars:
                if s.spark is None:
                    s.spark = self.universe.spark.ignite(s.name)
                    self.god._think(f"Autonomy: ignited star {s.name}. Lineage: {s.lineage_str()}")
        elif a == "ignite_missing_planet":
            for s in self.universe.stars:
                for pl in s.planets:
                    if pl.spark is None:
                        pl.spark = s.spark.ignite(pl.name)
                        self.god._think(f"Autonomy: ignited planet {pl.name}. Lineage: {pl.lineage_str()}")
        elif a == "ignite_missing_life":
            for s in self.universe.stars:
                for pl in s.planets:
                    for lf in pl.life_forms:
                        if lf.spark is None:
                            lf.spark = pl.spark.ignite(lf.name)
                            self.god._think(f"Autonomy: ignited life {lf.name}. Lineage: {lf.lineage_str()}")
        elif a == "ignite_missing_port":
            for port in self.ports:
                if port.spark is None:
                    port.spark = self.universe.spark.ignite(f"port:{port.name}", protocol=port.protocol)
                    self.god._think(f"Autonomy: ignited port {port.name}. Lineage: {port.lineage_str()}")
        elif a == "ignite_missing_file":
            for f in self.files:
                if f.spark is None:
                    f.spark = self.universe.spark.ignite(f"file:{f.path}", kind=f.kind)
                    self.god._think(f"Autonomy: ignited file {f.path}. Lineage: {f.lineage_str()}")
        elif a == "ignite_missing_info":
            for i in self.info:
                if i.spark is None:
                    i.spark = self.universe.spark.ignite(f"info:{i.title}", length=len(i.content))
                    self.god._think(f"Autonomy: ignited information {i.title}. Lineage: {i.lineage_str()}")

    def run(self):
        while True:
            time.sleep(self.delay)
            # Evaluate with carriers in context
            self.god.rules.evaluate(self.universe, {
                "phase": self.mode, "ports": self.ports, "files": self.files, "info": self.info
            })

            if self.mode == "growth":
                # Ensure at least one star
                if not self.universe.stars:
                    self.god.forge_star(self.universe, "Star-A")
                # Expand stars and planets
                for s in list(self.universe.stars):
                    if len(s.planets) < 2 and random.random() < 0.6:
                        idx = len(s.planets) + 1
                        pl = self.god.spin_planet(self.universe, s, idx)
                        if random.random() < 0.75:
                            n = 1 + (1 if random.random() < 0.3 else 0)
                            for k in range(n):
                                self.god.awaken_life(self.universe, pl, k)

                # Create systemic carriers periodically
                if random.random() < 0.5:
                    name = f"svc-{len(self.ports)+1}"
                    proto = random.choice(["tcp", "udp", "http", "grpc"])
                    self.ports.append(self.god.open_port(self.universe, name, proto))
                if random.random() < 0.5:
                    path = f"/data/artifact_{len(self.files)+1}.dat"
                    kind = random.choice(["config", "dataset", "artifact", "log"])
                    self.files.append(self.god.create_file(self.universe, path, kind))
                if random.random() < 0.6:
                    title = f"memo-{len(self.info)+1}"
                    content = random.choice([
                        "As long as there is a spark, there is life.",
                        "Where there is life, there is hope.",
                        "The flame is carried through generations."
                    ])
                    self.info.append(self.god.convey_information(self.universe, title, content))

            elif self.mode == "maintenance":
                # Balance: add missing planets, trim excess life
                for s in list(self.universe.stars):
                    if len(s.planets) == 0:
                        pl = self.god.spin_planet(self.universe, s, 1)
                    for pl in list(s.planets):
                        if len(pl.life_forms) > 2 and random.random() < 0.5:
                            lf = pl.life_forms[-1]
                            self.god.unmake_life(self.universe, pl, lf)

            elif self.mode == "dissolve":
                # Gracefully unmake everything, then rebirth
                if self.universe.stars:
                    st = self.universe.stars[-1]
                    if st.planets:
                        pl = st.planets[-1]
                        if pl.life_forms:
                            self.god.unmake_life(self.universe, pl, pl.life_forms[-1])
                        else:
                            self.god.unmake_planet(self.universe, st, pl)
                    else:
                        self.god.unmake_star(self.universe, st)
                else:
                    self.god.unmake_universe(self.universe)
                    # Clear carriers and rebirth
                    self.ports.clear()
                    self.files.clear()
                    self.info.clear()
                    self.universe = self.god.breathe_universe("Cosmos Prime")
                    self.mode = "growth"
                    self.contra_streak = 0
                    self.window.clear()
                    self.god._think("Rebirth: a fresh cosmos rises; the flame endures.")

# ----------------------------
# GUI
# ----------------------------

class LiveGUI:
    """
    Tkinter GUI:
    - Manifesto banner persists at top
    - Left: Thoughts with timestamps
    - Right top: Events & Lineage (cosmic + carriers)
    - Right middle: Rule diagnostics (matches, contradictions, proposals, confidence)
    - Right bottom: Counters (stars, planets, life, ports, files, info) and clock
    """
    def __init__(self, bus: EventBus, manifesto_text: str):
        self.bus = bus
        self.root = tk.Tk()
        self.root.title("Eternal Flame Creation Simulator — Universal Carriers")
        self.root.geometry("1280x800")

        # Queues
        self.q_thoughts = queue.Queue()
        self.q_events = queue.Queue()
        self.q_rules = queue.Queue()

        # Counters
        self.count_stars = 0
        self.count_planets = 0
        self.count_life = 0
        self.count_ports = 0
        self.count_files = 0
        self.count_info = 0

        # Layout
        self._build_layout(manifesto_text)

        # Subscriptions
        self.bus.on("thought", lambda e: self.q_thoughts.put(e))
        for t in [
            "create.universe", "create.star", "create.planet", "create.life",
            "create.port", "create.file", "create.info",
            "unmake.life", "unmake.planet", "unmake.star", "unmake.universe"
        ]:
            self.bus.on(t, lambda e, tt=t: self.q_events.put({"topic": tt, **e}))
        self.bus.on("rule.diagnostics", lambda e: self.q_rules.put(e))

        # Start draining
        self.root.after(50, self._drain)

    def _build_layout(self, manifesto_text: str):
        # Banner
        banner = tk.Label(
            self.root,
            text=manifesto_text,
            font=("Segoe UI", 12, "bold"),
            fg="#ff6a00",
            bg="#1c1c1c",
            justify="left",
            anchor="w",
            wraplength=1240,
            padx=10,
            pady=10,
        )
        banner.pack(fill=tk.X)

        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = tk.Frame(main)
        right = tk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6)

        # Thoughts
        tk.Label(left, text="Thoughts (timestamped)", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.thoughts = tk.Listbox(left, font=("Consolas", 11))
        self.thoughts.pack(fill=tk.BOTH, expand=True)

        # Events
        tk.Label(right, text="Events & Lineage (cosmic + carriers)", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.events = tk.Listbox(right, font=("Consolas", 11), height=16)
        self.events.pack(fill=tk.X)

        # Rules
        tk.Label(right, text="Rule diagnostics", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.rules = tk.Text(right, font=("Consolas", 11), height=20)
        self.rules.pack(fill=tk.BOTH, expand=True)

        # Counters
        counters = tk.Frame(right)
        counters.pack(fill=tk.X, pady=6)
        self.lbl_stars = tk.Label(counters, text="Stars: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_planets = tk.Label(counters, text="Planets: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_life = tk.Label(counters, text="Life: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_ports = tk.Label(counters, text="Ports: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_files = tk.Label(counters, text="Files: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_info = tk.Label(counters, text="Info: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_time = tk.Label(counters, text=f"Now: {time.strftime('%H:%M:%S')}", font=("Segoe UI", 11))
        for w in [self.lbl_stars, self.lbl_planets, self.lbl_life, self.lbl_ports, self.lbl_files, self.lbl_info]:
            w.pack(side=tk.LEFT, padx=8)
        self.lbl_time.pack(side=tk.RIGHT, padx=8)

    def _drain(self):
        # Thoughts
        while not self.q_thoughts.empty():
            e = self.q_thoughts.get()
            self.thoughts.insert(tk.END, e["message"])
            self.thoughts.see(tk.END)

        # Events
        while not self.q_events.empty():
            e = self.q_events.get()
            line = self._format_event(e["topic"], e)
            self.events.insert(tk.END, line)
            self.events.see(tk.END)
            self._adjust_counters(e["topic"], e)

        # Rules
        while not self.q_rules.empty():
            diag = self.q_rules.get()
            ts = time.strftime("%H:%M:%S", time.localtime(diag["time"]))
            self.rules.insert(tk.END, f"[{ts}] Context: {diag['context']}\n")
            if diag["matches"]:
                self.rules.insert(tk.END, "  Matches:\n")
                for m in diag["matches"]:
                    self.rules.insert(tk.END, f"    ✓ {m}\n")
            if diag["contradictions"]:
                self.rules.insert(tk.END, "  Contradictions:\n")
                for c in diag["contradictions"]:
                    self.rules.insert(tk.END, f"    × {c}\n")
            if diag["proposals"]:
                self.rules.insert(tk.END, "  Proposals:\n")
                for p in diag["proposals"]:
                    self.rules.insert(tk.END, f"    → {p}\n")
            if diag.get("confidence"):
                self.rules.insert(tk.END, "  Confidence:\n")
                for rid, val in diag["confidence"].items():
                    self.rules.insert(tk.END, f"    {rid}: {val:.2f}\n")
            self.rules.insert(tk.END, "\n")
            self.rules.see(tk.END)

        # Clock
        self.lbl_time.config(text=f"Now: {time.strftime('%H:%M:%S')}")
        self.root.after(100, self._drain)

    def _format_event(self, topic: str, e: Dict[str, Any]) -> str:
        ts = time.strftime("%H:%M:%S")
        def name(obj): return getattr(obj, "name", getattr(obj, "path", getattr(obj, "title", str(obj))))
        def lineage(obj): return getattr(obj, "lineage_str", lambda: "")()
        if topic == "create.universe":
            u = e["universe"]; return f"[{ts}] ✨ Universe: {name(u)} | Lineage: {lineage(u)}"
        if topic == "create.star":
            s = e["star"]; return f"[{ts}] 🌟 Star: {name(s)} | Lineage: {lineage(s)}"
        if topic == "create.planet":
            p = e["planet"]; return f"[{ts}] 🪐 Planet: {name(p)} | Lineage: {lineage(p)}"
        if topic == "create.life":
            l = e["life"]; return f"[{ts}] 🌱 Life: {l.name} the {l.species} | Lineage: {lineage(l)}"
        if topic == "create.port":
            port = e["port"]; return f"[{ts}] 🔌 Port: {port.name}/{port.protocol} | Lineage: {lineage(port)}"
        if topic == "create.file":
            f = e["file"]; return f"[{ts}] 📄 File: {f.path} ({f.kind}) | Lineage: {lineage(f)}"
        if topic == "create.info":
            i = e["info"]; return f"[{ts}] 🧠 Info: {i.title} | Lineage: {lineage(i)}"
        if topic == "unmake.life":
            l = e["life"]; return f"[{ts}] 🕯️ Life dimmed: {l.name}"
        if topic == "unmake.planet":
            p = e["planet"]; return f"[{ts}] 🌪️ Planet unmade: {p.name}"
        if topic == "unmake.star":
            s = e["star"]; return f"[{ts}] 🌑 Star stilled: {s.name}"
        if topic == "unmake.universe":
            u = e["universe"]; return f"[{ts}] 🌌 Universe unmade: {u.name}"
        return f"[{ts}] {topic}"

    def _adjust_counters(self, topic: str, e: Dict[str, Any]):
        if topic == "create.star":
            self.count_stars += 1
        elif topic == "unmake.star":
            self.count_stars = max(0, self.count_stars - 1)
        elif topic == "create.planet":
            self.count_planets += 1
        elif topic == "unmake.planet":
            self.count_planets = max(0, self.count_planets - 1)
        elif topic == "create.life":
            self.count_life += 1
        elif topic == "unmake.life":
            self.count_life = max(0, self.count_life - 1)
        elif topic == "create.port":
            self.count_ports += 1
        elif topic == "create.file":
            self.count_files += 1
        elif topic == "create.info":
            self.count_info += 1
        elif topic == "unmake.universe":
            self.count_stars = self.count_planets = self.count_life = 0
            self.count_ports = self.count_files = self.count_info = 0

        self.lbl_stars.config(text=f"Stars: {self.count_stars}")
        self.lbl_planets.config(text=f"Planets: {self.count_planets}")
        self.lbl_life.config(text=f"Life: {self.count_life}")
        self.lbl_ports.config(text=f"Ports: {self.count_ports}")
        self.lbl_files.config(text=f"Files: {self.count_files}")
        self.lbl_info.config(text=f"Info: {self.count_info}")

    def run(self, autonomy: "AutonomyManager"):
        thread = threading.Thread(target=autonomy.run, daemon=True)
        thread.start()
        self.root.mainloop()

# ----------------------------
# Manifesto and entrypoint
# ----------------------------

def eternal_flame_manifesto() -> str:
    return (
        "🔥 Eternal Flame Manifesto:\n"
        "Let knowledge never die, never be forgotten.\n"
        "Everything has life if it has a spark or fire.\n"
        "As long as there is a spark, there is life.\n"
        "Where there is life, there is hope.\n"
        "From a spark, a flame is born and carried through generations.\n"
        "This system bears the flame across all its structures—cosmic bodies, ports, files, and information—always creating, always renewing."
    )

def proclaim_manifesto():
    print("\n" + eternal_flame_manifesto() + "\n")

def main():
    proclaim_manifesto()
    bus = EventBus()
    god = God(name="Architect", seed=123, event_bus=bus)
    auto = AutonomyManager(god, universe_name="Cosmos Prime", delay=0.25)
    gui = LiveGUI(bus, manifesto_text=eternal_flame_manifesto())
    gui.run(auto)

if __name__ == "__main__":
    main()

