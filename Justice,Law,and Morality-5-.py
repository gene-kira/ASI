"""
humanity_code_gui_full.py

Stripped-down but complete engine:
- Principles, Action, HumanityCode (multi-principle evaluator)
- World with simple target simulation and risk snapshot
- Agents + Community deliberation producing real rationale text
- Orchestrator for loop wiring
- Tkinter GUI showing live epoch decisions and rationale
"""

import math
import random
import time
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

# ---------- Principles, Action, HumanityCode ----------

@dataclass(frozen=True)
class Principles:
    dignity: float = 1.0
    truth: float = 1.0
    non_harm: float = 1.0
    fairness: float = 1.0
    restoration: float = 1.0
    stewardship: float = 1.0
    humility: float = 1.0
    unity: float = 1.0
    def normalize(self) -> "Principles":
        total = sum(self.__dict__.values())
        if total == 0:
            return self
        scaled = {k: v / total for k, v in self.__dict__.items()}
        return Principles(**scaled)

@dataclass
class Action:
    label: str
    impacts: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    def clamp(self) -> "Action":
        clamped = {k: max(-1.0, min(1.0, v)) for k, v in self.impacts.items()}
        return Action(self.label, clamped, self.metadata)

@dataclass
class Evaluation:
    score: float
    per_dimension: Dict[str, float]
    explanation: List[str]

class HumanityCode:
    def __init__(self, principles: Optional[Principles] = None):
        self.principles = (principles or Principles()).normalize()
        self.priority_order = ["dignity","non_harm","truth","fairness","restoration","unity","humility","stewardship"]
    def evaluate(self, action: Action) -> Evaluation:
        a = action.clamp()
        weights = self.principles.__dict__
        per_dimension, explanation, score = {}, [], 0.0
        for i, dim in enumerate(self.priority_order):
            w = weights.get(dim, 0.0)
            v = a.impacts.get(dim, 0.0)
            boost = 1.0 + (0.05 * (len(self.priority_order) - i))
            contrib = w * v * boost
            per_dimension[dim] = contrib
            score += contrib
            explanation.append(f"[{dim}] impact={v:.2f}, weight={w:.2f}, boost={boost:.2f}, contrib={contrib:.3f}")
        core = ["dignity","non_harm","truth","fairness"]
        severe = sum(1 for d in core if a.impacts.get(d,0.0) < -0.7)
        if severe > 0:
            penalty = 0.15 * severe
            score -= penalty
            explanation.append(f"Penalty severe core: -{penalty:.3f}")
        restorative = sum(max(0.0, a.impacts.get(d, 0.0)) for d in ["restoration","unity","humility"])
        if restorative > 1.5:
            bonus = 0.1 * (restorative - 1.5)
            score += bonus
            explanation.append(f"Bonus restorative: +{bonus:.3f}")
        if a.impacts.get("stewardship", 0.0) < -0.5:
            score -= 0.08
            explanation.append("Penalty stewardship risk: -0.08")
        return Evaluation(score, per_dimension, explanation)
    def compare(self, actions: List[Action]) -> Tuple[Action, List[Tuple[Action, Evaluation]]]:
        evals = [(a, self.evaluate(a)) for a in actions]
        best = max(evals, key=lambda kv: kv[1].score)[0]
        return best, evals
    def explain_choice(self, best: Action, evals: List[Tuple[Action, Evaluation]]) -> str:
        lines = [f"Selected action: {best.label}"]
        for a, ev in evals:
            lines.append(f"- {a.label}: score={ev.score:.3f}")
        lines.append("Details:")
        for a, ev in evals:
            lines.append(f"  {a.label}:")
            for ln in ev.explanation:
                lines.append(f"    {ln}")
        return "\n".join(lines)

# ---------- World (targets + risk) ----------

@dataclass
class Target:
    tid: int
    x: float
    y: float
    kind: str = "civilian"
    last_seen: int = 0

@dataclass
class World:
    center_x: float = 0.0
    center_y: float = 0.0
    protected_radius: float = 5.0
    t: int = 0
    next_tid: int = 1
    targets: List[Target] = field(default_factory=list)

    def sense_simulated(self) -> List[Target]:
        # Create a few synthetic targets near or far from center
        new_targets = []
        for _ in range(random.randint(1, 3)):
            new_targets.append(Target(
                tid=self.next_tid,
                x=random.uniform(-6, 6),
                y=random.uniform(-6, 6),
                kind=random.choice(["civilian","unknown"]),
                last_seen=self.t + 1
            ))
            self.next_tid += 1
        if random.random() < 0.35:
            new_targets.append(Target(
                tid=self.next_tid,
                x=random.uniform(-3, 3),
                y=random.uniform(-3, 3),
                kind="aggressor",
                last_seen=self.t + 1
            ))
            self.next_tid += 1
        return new_targets

    def step(self):
        self.t += 1
        # Add new sensed targets (simple model — append then prune)
        self.targets.extend(self.sense_simulated())
        # Prune old targets
        self.targets = [t for t in self.targets if self.t - t.last_seen <= 20]

    def risk_snapshot(self) -> Dict[int, float]:
        risks: Dict[int, float] = {}
        for t in self.targets:
            base = 0.6 if t.kind == "aggressor" else 0.3 if t.kind == "unknown" else 0.1
            dx, dy = t.x - self.center_x, t.y - self.center_y
            dist = math.hypot(dx, dy)
            near = max(0.0, (self.protected_radius - dist) / max(self.protected_radius, 1e-6))
            risk = base + 0.25 * near
            risks[t.tid] = max(0.0, min(1.0, risk))
        return risks

# ---------- Agents + Community ----------

@dataclass
class Agent:
    name: str
    temperament: Dict[str, float]
    trust: float = 0.5
    def propose_actions(self, ctx: Dict[str, Any], risk_report: Dict[int, float]) -> List[Action]:
        tid = max(risk_report, key=risk_report.get) if risk_report else None
        risk = risk_report.get(tid, 0.0) if tid is not None else 0.0
        return [
            Action(f"{self.name}: De-escalate {tid}", {"dignity":0.8,"non_harm":0.9,"restoration":0.8,"unity":0.7}, {"type":"restorative","target":tid,"risk":risk}),
            Action(f"{self.name}: Protective {tid}", {"dignity":0.6,"non_harm":0.6,"stewardship":0.6,"fairness":0.6}, {"type":"protective","target":tid,"risk":risk}),
            Action(f"{self.name}: Punitive {tid}", {"dignity":0.1,"non_harm":-0.5,"unity":-0.4,"humility":-0.2}, {"type":"punitive","target":tid,"risk":risk}),
        ]
    def adapt(self, outcome: float, decision_type: str):
        if decision_type == "restorative":
            self.trust = max(0.0, min(1.0, self.trust + 0.05 * outcome))

@dataclass
class Community:
    name: str
    code: HumanityCode
    agents: List[Agent]
    def deliberate(self, ctx: Dict[str, Any], risk_report: Dict[int, float]) -> Dict[str, Any]:
        proposals: List[Action] = []
        for a in self.agents:
            proposals.extend(a.propose_actions(ctx, risk_report))
        best, evals = self.code.compare(proposals)
        return {"decision": best.label, "rationale": self.code.explain_choice(best, evals), "metadata": best.metadata}
    def restorative_update(self, outcome: float, decision_type: str):
        for a in self.agents:
            a.adapt(outcome, decision_type)

# ---------- Orchestrator ----------

class Orchestrator:
    def __init__(self, community: Community, world: World):
        self.community = community
        self.world = world
        self.epoch = 0
    def synthesize_context(self) -> Dict[str, Any]:
        return {"center_x": self.world.center_x, "center_y": self.world.center_y, "protected_radius": self.world.protected_radius}
    def step(self) -> Tuple[int, Dict[int, float], Dict[str, Any], Dict[str, Any], float]:
        self.epoch += 1
        self.world.step()
        risks = self.world.risk_snapshot()
        ctx = self.synthesize_context()
        decision = self.community.deliberate(ctx, risks)
        dtype = decision.get("metadata", {}).get("type", "restorative")
        risk = decision.get("metadata", {}).get("risk", 0.0)
        base = {"restorative":0.8, "protective":0.55, "punitive":-0.25}.get(dtype, 0.3)
        outcome = max(-1.0, min(1.0, base - 0.25 * risk + random.uniform(-0.15, 0.15)))
        self.community.restorative_update(outcome, dtype)
        return self.epoch, risks, ctx, decision, outcome

# ---------- GUI ----------

class HumanityGUI(tk.Tk):
    def __init__(self, orch: Orchestrator):
        super().__init__()
        self.orch = orch
        self.title("Humanity Code Dashboard (Stripped-down, Real Deliberation)")
        self.geometry("800x600")

        # scrolling log
        self.log = ScrolledText(self, wrap="word", font=("Courier", 10))
        self.log.pack(fill="both", expand=True)

        # Start background loop
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            epoch, risks, ctx, decision, outcome = self.orch.step()
            # Decide color based on decision type
            dtype = decision.get("metadata", {}).get("type", "restorative")
            color = {"restorative":"#1f7a1f", "protective":"#a67c00", "punitive":"#a61f1f"}.get(dtype, "#333333")
            header = f"Epoch {epoch}: {decision['decision']} outcome={outcome:.2f} type={dtype}\n"
            rationale = decision["rationale"]
            # Insert colored header, plain rationale
            self.log.insert(tk.END, header, ("hdr",))
            self.log.insert(tk.END, rationale + "\n\n")
            self.log.tag_config("hdr", foreground=color)
            self.log.see(tk.END)
            time.sleep(1)

# ---------- Build and run ----------

def build_default_community() -> Community:
    principles = Principles(dignity=1.2, truth=1.1, non_harm=1.3, fairness=1.0, restoration=1.2, stewardship=0.9, humility=1.0, unity=1.1).normalize()
    code = HumanityCode(principles)
    agents = [
        Agent("Ava", {"assertiveness":0.4,"compassion":0.8,"prudence":0.7}, trust=0.6),
        Agent("Rex", {"assertiveness":0.7,"compassion":0.5,"prudence":0.6}, trust=0.5),
        Agent("Sol", {"assertiveness":0.5,"compassion":0.7,"prudence":0.8}, trust=0.7),
    ]
    return Community("Hearth", code, agents)

def build_default_world() -> World:
    return World(center_x=0.0, center_y=0.0, protected_radius=5.0)

if __name__ == "__main__":
    community = build_default_community()
    world = build_default_world()
    orch = Orchestrator(community, world)
    app = HumanityGUI(orch)
    app.mainloop()

