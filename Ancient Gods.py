#!/usr/bin/env python3
"""
Godlike Creation Simulator — Live GUI
- Auto-loader ensures dependencies are present
- Event bus with thought, rule, and lifecycle telemetry
- Threaded simulation, non-blocking Tkinter GUI
- Surfaces: thoughts, rule matches, contradictions, corrective proposals, timestamps
"""

# ----------------------------
# Auto-loader
# ----------------------------

import importlib
import subprocess
import sys

REQUIRED_LIBS = [
    "random",
    "time",
    "dataclasses",
    "typing",
    "threading",
    "queue",
    "tkinter",
]

def ensure_libs(libs):
    loaded = {}
    for lib in libs:
        try:
            loaded[lib] = importlib.import_module(lib)
        except ImportError:
            print(f"Missing {lib}, attempting to install (pip).")
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

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Optional

# ----------------------------
# Event bus
# ----------------------------

class EventBus:
    """Simple publish/subscribe for creation, thoughts, and rule telemetry."""
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

@dataclass
class LifeForm:
    name: str
    species: str
    born_at: float = field(default_factory=time.time)

@dataclass
class Planet:
    name: str
    life_forms: List[LifeForm] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class Star:
    name: str
    planets: List[Planet] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class Universe:
    name: str
    stars: List[Star] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

# ----------------------------
# Rule engine (matches, contradictions, corrective proposals)
# ----------------------------

class RuleEngine:
    """
    Minimal rule system that evaluates intents and states, producing:
    - matches: rules satisfied
    - contradictions: rules violated
    - corrective proposals: suggested actions to resolve contradictions
    """
    def __init__(self, event_bus: EventBus):
        self.bus = event_bus

    def evaluate(self, universe: Universe, context: Dict[str, Any]):
        matches = []
        contradictions = []
        proposals = []

        # Example rules:
        # R1: A star should have at least 1 planet within the first two creations
        star: Optional[Star] = context.get("star")
        if star:
            if len(star.planets) >= 1:
                matches.append(f"R1: {star.name} has >=1 planet.")
            else:
                contradictions.append(f"R1: {star.name} has 0 planets.")
                proposals.append(f"Propose: add planet to {star.name}.")

        # R2: Planet may awaken life if intention says so and random favors
        planet: Optional[Planet] = context.get("planet")
        intended_life_count = context.get("intended_life_count")
        if planet is not None and intended_life_count is not None:
            if intended_life_count > 0:
                if len(planet.life_forms) >= intended_life_count:
                    matches.append(f"R2: {planet.name} met intended life ({intended_life_count}).")
                else:
                    contradictions.append(f"R2: {planet.name} life below intent ({len(planet.life_forms)}/{intended_life_count}).")
                    proposals.append(f"Propose: awaken more life on {planet.name}.")
            else:
                if len(planet.life_forms) == 0:
                    matches.append(f"R2: {planet.name} correctly has no life.")
                else:
                    contradictions.append(f"R2: {planet.name} has life despite intent 0.")
                    proposals.append(f"Propose: pause further awakening on {planet.name}.")

        # R3: Universe must retain at least one star until finale
        if context.get("phase") != "finale":
            if len(universe.stars) >= 1:
                matches.append("R3: Universe retains at least one star.")
            else:
                contradictions.append("R3: Universe has no stars mid-creation.")
                proposals.append("Propose: forge a star before proceeding.")

        # Emit diagnostics
        diag = {
            "time": time.time(),
            "matches": matches,
            "contradictions": contradictions,
            "proposals": proposals,
            "context": {
                k: v.name if hasattr(v, "name") else v
                for k, v in context.items()
            }
        }
        self.bus.emit("rule.diagnostics", diag)

# ----------------------------
# God orchestrator
# ----------------------------

class God:
    """
    Creator with auditable thoughts and symmetric create/unmake operations.
    Integrates with RuleEngine to surface matches, contradictions, and proposals.
    """
    def __init__(self, name: str = "Architect", seed: Optional[int] = None, event_bus: Optional[EventBus] = None):
        self.name = name
        self.bus = event_bus or EventBus()
        self.thoughts: List[str] = []
        self.rules = RuleEngine(self.bus)
        if seed is not None:
            random.seed(seed)
            self._think(f"Seed set to {seed} for reproducible creation.")
        else:
            self._think("No seed provided; creation embraces chance.")

    def _emit(self, topic: str, **kwargs):
        self.bus.emit(topic, {"by": self.name, **kwargs})

    def _ts(self) -> str:
        return time.strftime("%H:%M:%S")

    def _think(self, msg: str, kind: str = "thought"):
        entry = f"[{self._ts()}] {msg}"
        self.thoughts.append(entry)
        self._emit(kind, message=entry, kind=kind)

    # Creation
    def breathe_universe(self, name: str) -> Universe:
        self._think(f"In the beginning, naming the cosmos '{name}'.", kind="thought")
        universe = Universe(name=name)
        self._emit("create.universe", universe=universe)
        self.rules.evaluate(universe, {"phase": "init"})
        return universe

    def forge_star(self, universe: Universe, name: str) -> Star:
        self._think(f"Gathering dust and destiny into a star called {name}.", kind="thought")
        star = Star(name=name)
        universe.stars.append(star)
        self._emit("create.star", star=star, universe=universe)
        self.rules.evaluate(universe, {"star": star, "phase": "forge_star"})
        return star

    def spin_planet(self, star: Star, index: int, universe: Universe) -> Planet:
        pname = f"{star.name}-Planet-{index}"
        self._think(f"Cooling rings and storms into a world named {pname}.", kind="thought")
        planet = Planet(name=pname)
        star.planets.append(planet)
        self._emit("create.planet", planet=planet, star=star, universe=universe)
        self.rules.evaluate(universe, {"star": star, "planet": planet, "phase": "spin_planet"})
        return planet

    def awaken_life(self, planet: Planet, k: int, universe: Universe):
        species = random.choice(["Elemental", "Wanderer", "Seeker", "Archivist", "Tidemind"])
        lname = f"Being-{chr(97 + (k % 26))}"
        self._think(f"Kindling awareness: '{lname} the {species}' on {planet.name}.", kind="thought")
        life = LifeForm(name=lname, species=species)
        planet.life_forms.append(life)
        self._emit("create.life", life=life, planet=planet, universe=universe)
        self.rules.evaluate(universe, {"planet": planet, "phase": "awaken_life", "intended_life_count": None})
        return life

    # Unmaking
    def unmake_life(self, planet: Planet, life: LifeForm, universe: Universe):
        self._think(f"Softly closing the chapter of {life.name} the {life.species} on {planet.name}.", kind="thought")
        planet.life_forms = [l for l in planet.life_forms if l is not life]
        self._emit("unmake.life", life=life, planet=planet, universe=universe)
        self.rules.evaluate(universe, {"planet": planet, "phase": "unmake_life"})

    def unmake_planet(self, star: Star, planet: Planet, universe: Universe):
        self._think(f"Drawing back the seas and skies of {planet.name}.", kind="thought")
        star.planets = [p for p in star.planets if p is not planet]
        self._emit("unmake.planet", planet=planet, star=star, universe=universe)
        self.rules.evaluate(universe, {"star": star, "phase": "unmake_planet"})

    def unmake_star(self, universe: Universe, star: Star):
        self._think(f"Letting the light of {star.name} fall into quiet.", kind="thought")
        universe.stars = [s for s in universe.stars if s is not star]
        self._emit("unmake.star", star=star, universe=universe)
        self.rules.evaluate(universe, {"phase": "unmake_star"})

    def unmake_universe(self, universe: Universe):
        self._think(f"Unwriting the name of {universe.name}. All returns to stillness.", kind="thought")
        universe.stars.clear()
        self._emit("unmake.universe", universe=universe)
        self.rules.evaluate(universe, {"phase": "finale"})

# ----------------------------
# Simulation (background thread)
# ----------------------------

def creation_scenario(god: God, seed: Optional[int] = 123, delay: float = 0.35):
    if seed is not None:
        random.seed(seed)
        god._think(f"Scenario seed set to {seed}.", kind="thought")

    u = god.breathe_universe("Cosmos Prime")
    time.sleep(delay)

    # Forge stars and planets with intent signals and rule evaluation
    for i in range(3):
        star = god.forge_star(u, f"Star-{chr(65 + i)}")
        time.sleep(delay)

        n_planets = random.randint(1, 3)
        god._think(f"Intent: {star.name} will host {n_planets} planet(s).", kind="thought")
        god.rules.evaluate(u, {"star": star, "phase": "intent_star_planets"})

        for j in range(1, n_planets + 1):
            planet = god.spin_planet(star, j, u)
            time.sleep(delay)

            if random.random() < 0.7:
                n_life = random.randint(1, 2)
                god._think(f"Chance favors awakening: {planet.name} expects {n_life} life form(s).", kind="thought")
                god.rules.evaluate(u, {"planet": planet, "phase": "intent_planet_life", "intended_life_count": n_life})
                for k in range(n_life):
                    god.awaken_life(planet, k, u)
                    time.sleep(delay)
            else:
                god._think(f"No awakening on {planet.name}; its seas dream alone.", kind="thought")
                god.rules.evaluate(u, {"planet": planet, "phase": "intent_planet_life", "intended_life_count": 0})
                time.sleep(delay)

    # Demonstrate unmaking a single life and a planet
    if u.stars and u.stars[0].planets and u.stars[0].planets[0].life_forms:
        planet0 = u.stars[0].planets[0]
        life0 = planet0.life_forms[0]
        god.unmake_life(planet0, life0, u)
        time.sleep(delay)

    if len(u.stars) > 1 and u.stars[1].planets:
        god.unmake_planet(u.stars[1], u.stars[1].planets[-1], u)
        time.sleep(delay)

    # Finale
    if u.stars:
        god.unmake_star(u, u.stars[-1])
        time.sleep(delay)
    god.unmake_universe(u)

# ----------------------------
# GUI
# ----------------------------

class LiveGUI:
    """
    Tkinter GUI:
    - Left: Thoughts (kind-tagged)
    - Right top: Events feed (create/unmake)
    - Right middle: Rule diagnostics (matches, contradictions, proposals)
    - Right bottom: Timeline counters (stars, planets, life)
    """
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.root = tk.Tk()
        self.root.title("Godlike Creation — Live Telemetry")
        self.root.geometry("1100x700")

        # Queues for thread-safe GUI updates
        self.q_thoughts = queue.Queue()
        self.q_events = queue.Queue()
        self.q_rules = queue.Queue()

        # Counters
        self.count_stars = 0
        self.count_planets = 0
        self.count_life = 0

        # Layout
        self._build_layout()

        # Bind bus to queues (no direct UI updates from non-main thread)
        self.bus.on("thought", lambda e: self.q_thoughts.put(e))
        for topic in [
            "create.universe", "create.star", "create.planet",
            "create.life", "unmake.life", "unmake.planet",
            "unmake.star", "unmake.universe"
        ]:
            self.bus.on(topic, lambda e, t=topic: self.q_events.put({"topic": t, **e}))
        self.bus.on("rule.diagnostics", lambda e: self.q_rules.put(e))

        # Poll queues
        self.root.after(50, self._drain_queues)

    def _build_layout(self):
        # Frames
        left = tk.Frame(self.root)
        right = tk.Frame(self.root)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Thoughts panel
        tk.Label(left, text="Thoughts, contradictions, proposals (timestamped)", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.thoughts_list = tk.Listbox(left, font=("Consolas", 11))
        self.thoughts_list.pack(fill=tk.BOTH, expand=True)
        self.thoughts_list_scroll = tk.Scrollbar(self.thoughts_list, orient=tk.VERTICAL, command=self.thoughts_list.yview)
        self.thoughts_list.config(yscrollcommand=self.thoughts_list_scroll.set)

        # Events panel
        tk.Label(right, text="Creation & unmaking events", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.events_list = tk.Listbox(right, font=("Consolas", 11), height=12)
        self.events_list.pack(fill=tk.X)

        # Rule diagnostics panel
        tk.Label(right, text="Rule diagnostics", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.rules_text = tk.Text(right, font=("Consolas", 11), height=18)
        self.rules_text.pack(fill=tk.BOTH, expand=True)

        # Timeline counters
        counters = tk.Frame(right)
        counters.pack(fill=tk.X, pady=6)
        self.lbl_stars = tk.Label(counters, text="Stars: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_planets = tk.Label(counters, text="Planets: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_life = tk.Label(counters, text="Life: 0", font=("Segoe UI", 11, "bold"))
        self.lbl_time = tk.Label(counters, text=f"Now: {time.strftime('%H:%M:%S')}", font=("Segoe UI", 11))
        self.lbl_stars.pack(side=tk.LEFT, padx=8)
        self.lbl_planets.pack(side=tk.LEFT, padx=8)
        self.lbl_life.pack(side=tk.LEFT, padx=8)
        self.lbl_time.pack(side=tk.RIGHT, padx=8)

    def _drain_queues(self):
        # Thoughts
        while not self.q_thoughts.empty():
            e = self.q_thoughts.get()
            kind = e.get("kind", "thought")
            msg = e["message"]
            tag = {"thought": "•", "contradiction": "×", "proposal": "→"}.get(kind, "•")
            self.thoughts_list.insert(tk.END, f"{tag} {msg}")
            self.thoughts_list.see(tk.END)

        # Events
        while not self.q_events.empty():
            e = self.q_events.get()
            topic = e["topic"]
            line = self._format_event_line(topic, e)
            self.events_list.insert(tk.END, line)
            self.events_list.see(tk.END)
            self._adjust_counters(topic, e)

        # Rules
        while not self.q_rules.empty():
            diag = self.q_rules.get()
            ts = time.strftime("%H:%M:%S", time.localtime(diag["time"]))
            self.rules_text.insert(tk.END, f"[{ts}] Context: {diag['context']}\n")
            if diag["matches"]:
                self.rules_text.insert(tk.END, "  Matches:\n")
                for m in diag["matches"]:
                    self.rules_text.insert(tk.END, f"    ✓ {m}\n")
            if diag["contradictions"]:
                self.rules_text.insert(tk.END, "  Contradictions:\n")
                for c in diag["contradictions"]:
                    self.rules_text.insert(tk.END, f"    × {c}\n")
                    # Also send contradiction to thoughts pane
                    self.thoughts_list.insert(tk.END, f"× [{ts}] {c}")
            if diag["proposals"]:
                self.rules_text.insert(tk.END, "  Proposals:\n")
                for p in diag["proposals"]:
                    self.rules_text.insert(tk.END, f"    → {p}\n")
                    # Also send proposal to thoughts pane
                    self.thoughts_list.insert(tk.END, f"→ [{ts}] {p}")
            self.rules_text.insert(tk.END, "\n")
            self.rules_text.see(tk.END)

        # Update clock
        self.lbl_time.config(text=f"Now: {time.strftime('%H:%M:%S')}")

        # Schedule next poll
        self.root.after(100, self._drain_queues)

    def _format_event_line(self, topic: str, e: Dict[str, Any]) -> str:
        ts = time.strftime("%H:%M:%S")
        def name(obj):
            return getattr(obj, "name", str(obj))
        if topic == "create.universe":
            return f"[{ts}] ✨ Universe created: {name(e['universe'])}"
        if topic == "create.star":
            return f"[{ts}] 🌟 Star forged: {name(e['star'])}"
        if topic == "create.planet":
            return f"[{ts}] 🪐 Planet spun: {name(e['planet'])} (around {name(e['star'])})"
        if topic == "create.life":
            life = e['life']
            return f"[{ts}] 🌱 Life awakens: {life.name} the {life.species} on {name(e['planet'])}"
        if topic == "unmake.life":
            life = e['life']
            return f"[{ts}] 🕯️ Life dimmed: {life.name} returns to memory on {name(e['planet'])}"
        if topic == "unmake.planet":
            return f"[{ts}] 🌪️ Planet unmade: {name(e['planet'])} from {name(e['star'])}"
        if topic == "unmake.star":
            return f"[{ts}] 🌑 Star stilled: {name(e['star'])}"
        if topic == "unmake.universe":
            return f"[{ts}] 🌌 Universe unmade: {name(e['universe'])}"
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
        elif topic == "unmake.universe":
            self.count_stars = 0
            self.count_planets = 0
            self.count_life = 0

        self.lbl_stars.config(text=f"Stars: {self.count_stars}")
        self.lbl_planets.config(text=f"Planets: {self.count_planets}")
        self.lbl_life.config(text=f"Life: {self.count_life}")

    def run(self, scenario_fn: Callable[[God], None], seed: Optional[int] = 123):
        # Instantiate God and start scenario in a background thread
        bus = self.bus
        god = God(name="Architect", seed=seed, event_bus=bus)

        thread = threading.Thread(target=lambda: scenario_fn(god), daemon=True)
        thread.start()

        self.root.mainloop()

# ----------------------------
# Entrypoint
# ----------------------------

def main():
    bus = EventBus()
    gui = LiveGUI(bus)
    gui.run(lambda g: creation_scenario(g, seed=123, delay=0.3))

if __name__ == "__main__":
    main()

