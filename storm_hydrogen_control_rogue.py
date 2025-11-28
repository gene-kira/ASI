# storm_hydrogen_control_rogue.py
# Storm-aware hydrogen control system with Rogue Drift perturbations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List
import time, threading, random

# =========================
# Event bus and data types
# =========================

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Any], None]]] = {}

    def publish(self, topic: str, payload: Any):
        for cb in self._subs.get(topic, []):
            try:
                cb(payload)
            except Exception as e:
                print(f"[bus] handler error on {topic}: {e}")

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        self._subs.setdefault(topic, []).append(callback)

@dataclass
class SensorFrame:
    ts: float
    lightning_proximity_km: float
    strike_density_per_min: float
    wind_speed_ms: float
    wind_gust_ms: float
    precipitation_mmph: float
    grid_freq_hz: float
    grid_volt_v: float
    price_usd_mwh: float
    curtailment_signal: bool

@dataclass
class ProcessFrame:
    ts: float
    stack_temp_c: float
    stack_pressure_bar: float
    stack_current_a: float
    h2_purity_pct: float
    h2_soc_pct: float
    battery_soc_pct: float
    water_cond_uScm: float
    water_turbidity_ntu: float
    cooling_nominal: bool

@dataclass
class RiskFrame:
    ts: float
    storm_risk: float
    grid_volatility: float
    stress_score: float

@dataclass
class Command:
    name: str
    args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GuiSignal:
    ts: float
    topic: str
    data: Dict[str, Any]

# =========
# Sensors
# =========

class StormSensors:
    def __init__(self, bus: EventBus, interval: float = 0.75):
        self.bus = bus
        self.interval = interval
        self._stop = False

    def start(self):
        def loop():
            while not self._stop:
                sf = SensorFrame(
                    ts=time.time(),
                    lightning_proximity_km=random.uniform(1, 50),
                    strike_density_per_min=random.uniform(0, 20),
                    wind_speed_ms=random.uniform(2, 25),
                    wind_gust_ms=random.uniform(3, 35),
                    precipitation_mmph=random.uniform(0, 10),
                    grid_freq_hz=random.uniform(59.3, 60.7),
                    grid_volt_v=random.uniform(110000, 125000),
                    price_usd_mwh=random.uniform(-20, 200),
                    curtailment_signal=random.random() < 0.1
                )
                self.bus.publish("sensor.storm", sf)
                time.sleep(self.interval)
        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._stop = True

class ProcessSensors:
    def __init__(self, bus: EventBus, interval: float = 0.75):
        self.bus = bus
        self.interval = interval
        self._stop = False

    def start(self):
        def loop():
            stack_temp = 40.0
            stack_pressure = 20.0
            soc_h2 = 50.0
            soc_batt = 50.0
            while not self._stop:
                stack_temp += random.uniform(-0.5, 0.8)
                stack_pressure += random.uniform(-0.2, 0.3)
                soc_h2 += random.uniform(-0.3, 0.6)
                soc_batt += random.uniform(-0.6, 0.6)
                pf = ProcessFrame(
                    ts=time.time(),
                    stack_temp_c=max(20, stack_temp),
                    stack_pressure_bar=max(5, stack_pressure),
                    stack_current_a=random.uniform(50, 500),
                    h2_purity_pct=random.uniform(98, 100),
                    h2_soc_pct=min(max(soc_h2, 0), 100),
                    battery_soc_pct=min(max(soc_batt, 0), 100),
                    water_cond_uScm=random.uniform(0.1, 10.0),
                    water_turbidity_ntu=random.uniform(0.0, 5.0),
                    cooling_nominal=True
                )
                self.bus.publish("sensor.process", pf)
                time.sleep(self.interval)
        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._stop = True

# =====================
# Models and heuristics
# =====================

def compute_storm_risk(sf: SensorFrame) -> float:
    prox = max(0, 1 - (sf.lightning_proximity_km / 50))
    density = min(sf.strike_density_per_min / 20, 1.0)
    gust = min(sf.wind_gust_ms / 35, 1.0)
    wx = min(sf.precipitation_mmph / 10, 1.0)
    return min(1.0, 0.35*prox + 0.35*density + 0.2*gust + 0.1*wx)

def compute_grid_volatility(sf: SensorFrame) -> float:
    freq_dev = min(abs(sf.grid_freq_hz - 60.0) / 0.7, 1.0)
    volt_dev = min(abs(sf.grid_volt_v - 118000) / 8000, 1.0)
    price = 0.0 if sf.price_usd_mwh >= 0 else min(abs(sf.price_usd_mwh) / 50, 1.0)
    curt = 1.0 if sf.curtailment_signal else 0.0
    return min(1.0, 0.4*freq_dev + 0.3*volt_dev + 0.2*price + 0.1*curt)

def compute_stress(pf: ProcessFrame) -> float:
    temp = max(0, (pf.stack_temp_c - 60) / 30)
    pressure = max(0, (pf.stack_pressure_bar - 30) / 10)
    purity = max(0, (99.5 - pf.h2_purity_pct) / 1.5)
    return min(1.0, 0.5*temp + 0.3*pressure + 0.2*purity)

def make_risk_frame(sf: SensorFrame, pf: ProcessFrame) -> RiskFrame:
    return RiskFrame(
        ts=sf.ts,
        storm_risk=compute_storm_risk(sf),
        grid_volatility=compute_grid_volatility(sf),
        stress_score=compute_stress(pf)
    )

# =================
# Safety interlocks
# =================

SAFE_LIMITS = {
    "stack_temp_c_max": 85.0,
    "stack_pressure_bar_max": 35.0,
    "stack_current_a_max": 600.0,
    "h2_soc_pct_max": 98.0,
    "battery_soc_pct_min": 10.0,
    "water_cond_uScm_max": 5.0,
    "water_turbidity_ntu_max": 1.0
}

def check_interlocks(pf: ProcessFrame) -> dict:
    return {
        "cooling_nominal": pf.cooling_nominal,
        "water_quality_ok": (pf.water_cond_uScm <= SAFE_LIMITS["water_cond_uScm_max"]
                             and pf.water_turbidity_ntu <= SAFE_LIMITS["water_turbidity_ntu_max"]),
        "stack_within_limits": (pf.stack_temp_c <= SAFE_LIMITS["stack_temp_c_max"]
                                and pf.stack_pressure_bar <= SAFE_LIMITS["stack_pressure_bar_max"])
    }

def hard_violation(pf: ProcessFrame) -> bool:
    return (
        pf.stack_temp_c > SAFE_LIMITS["stack_temp_c_max"] or
        pf.stack_pressure_bar > SAFE_LIMITS["stack_pressure_bar_max"] or
        pf.h2_soc_pct > SAFE_LIMITS["h2_soc_pct_max"]
    )

# ===========
# Rogue Drift
# ===========

class RogueDrift:
    def __init__(self, intensity=0.07, seed=None):
        self.intensity = intensity
        if seed is not None:
            random.seed(seed)

    def perturb(self, value: float, min_val: float, max_val: float) -> float:
        drift = (random.random() - 0.5) * 2 * self.intensity * (max_val - min_val)
        new_val = value + drift
        return max(min_val, min(max_val, new_val))

    def drift_profile(self, profile: dict) -> dict:
        drifted = {}
        for k, v in profile.items():
            if isinstance(v, (int, float)):
                drifted[k] = self.perturb(v, v*0.9, v*1.1)
            else:
                drifted[k] = v
        return drifted

# ===========
# Controller
# ===========

class Controller:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.state = "OBSERVE"
        self.last_transition = time.time()
        self.sf: SensorFrame | None = None
        self.pf: ProcessFrame | None = None
        self.rf: RiskFrame | None = None
        self.rogue = RogueDrift(intensity=0.07)  # Rogue drift engine

        bus.subscribe("sensor.storm", self.on_storm)
        bus.subscribe("sensor.process", self.on_process)

    def on_storm(self, sf: SensorFrame):
        self.sf = sf
        self.evaluate()

    def on_process(self, pf: ProcessFrame):
        self.pf = pf
        self.evaluate()

    def evaluate(self):
        if not (self.sf and self.pf):
            return
        self.rf = make_risk_frame(self.sf, self.pf)

        interlocks = check_interlocks(self.pf)
        violation = hard_violation(self.pf)

        # State transitions
        if violation or self.rf.stress_score >= 0.9 or not interlocks["cooling_nominal"]:
            self.transition("PROTECT")
        elif self.island_required():
            self.transition("ISLAND")
        elif self.state in ["OBSERVE", "RECOVER"] and (self.rf.storm_risk >= 0.5 or self.rf.grid_volatility >= 0.5):
            self.transition("PREPARE")
        elif self.state == "PREPARE" and self.surplus_or_wind_surge():
            self.transition("ABSORB")
        elif self.state in ["ABSORB", "ISLAND"] and self.recover_window():
            self.transition("RECOVER")

        # Actions
        self.act(interlocks)

        # GUI
        self.emit_gui()

    def transition(self, new_state: str):
        if new_state != self.state:
            self.last_transition = time.time()
            self.state = new_state
            self.bus.publish("controller.event", {"type": "transition", "to": new_state})

    # Triggers
    def island_required(self) -> bool:
        freq_dev = abs(self.sf.grid_freq_hz - 60.0) > 0.5
        volt_dev = abs(self.sf.grid_volt_v - 118000) > 6000
        return freq_dev or volt_dev

    def surplus_or_wind_surge(self) -> bool:
        gust_ok = self.sf.wind_gust_ms >= 20.0
        curtail = self.sf.curtailment_signal or self.sf.price_usd_mwh < 0
        batt_headroom = self.pf.battery_soc_pct <= 90.0
        h2_headroom = self.pf.h2_soc_pct <= 95.0
        return (gust_ok or curtail) and (batt_headroom or h2_headroom)

    def recover_window(self) -> bool:
        stable = (
            self.rf.storm_risk < 0.3 and
            self.rf.grid_volatility < 0.3 and
            self.rf.stress_score < 0.5
        )
        dwell = (time.time() - self.last_transition) > 10
        return stable and dwell

    # Actions
    def act(self, interlocks: dict):
        if self.state == "OBSERVE":
            self.optimize_dispatch()
        elif self.state == "PREPARE":
            if interlocks["stack_within_limits"]:
                self.pre_cool()
                self.free_headroom()
                self.ready_stormwater()
        elif self.state == "ABSORB":
            if interlocks["water_quality_ok"] and interlocks["stack_within_limits"]:
                self.ramp_electrolyzers_fast()
                self.battery_smooth()
                self.process_rain_nitrates()
        elif self.state == "ISLAND":
            self.isolate_microgrid()
            self.hold_h2_output()
            self.shed_noncritical()
            self.route_h2_downstream_or_flare()
        elif self.state == "PROTECT":
            self.downramp_purge_cool()
            self.run_diagnostics()
        elif self.state == "RECOVER":
            self.slow_ramp_resume()
            self.tune_models()
            self.reconcile_inventories()

    # Command stubs with Rogue Drift
    def optimize_dispatch(self):
        self.bus.publish("command", Command("optimize_dispatch"))

    def pre_cool(self):
        self.bus.publish("command", Command("increase_coolant_flow", {"target_temp_c": 45}))

    def free_headroom(self):
        self.bus.publish("command", Command("discharge_battery_to_mid_soc", {"target_soc_pct": 50}))
        self.bus.publish("command", Command("route_h2_downstream", {"mode": "ammonia_if_available"}))

    def ready_stormwater(self):
        self.bus.publish("command", Command("open_stormwater_intake", {"pretreatment": True}))

    def ramp_electrolyzers_fast(self):
        profile = {"profile": "FAST", "cap": SAFE_LIMITS["stack_current_a_max"]}
        drifted = self.rogue.drift_profile(profile)
        self.bus.publish("command", Command("ramp_electrolyzer", drifted))

    def battery_smooth(self):
        self.bus.publish("command", Command("battery_smooth_transients"))

    def process_rain_nitrates(self):
        self.bus.publish("command", Command("concentrate_nitrates", {"rate": "auto"}))

    def isolate_microgrid(self):
        self.bus.publish("command", Command("open_breakers_island"))

    def hold_h2_output(self):
        self.bus.publish("command", Command("hold_h2_output_within_limits"))

    def shed_noncritical(self):
        self.bus.publish("command", Command("shed_noncritical_loads"))

    def route_h2_downstream_or_flare(self):
        self.bus.publish("command", Command("route_h2_downstream_or_flare", {"priority": ["ammonia","methanol","flare"]}))

    def downramp_purge_cool(self):
        self.bus.publish("command", Command("controlled_downramp"))
        self.bus.publish("command", Command("purge_stacks"))
        self.bus.publish("command", Command("maximize_cooling"))

    def run_diagnostics(self):
        self.bus.publish("command", Command("run_integrity_checks"))

    def slow_ramp_resume(self):
        profile = {"profile": "SLOW", "cap": SAFE_LIMITS["stack_current_a_max"]*0.7}
        drifted = self.rogue.drift_profile(profile)
        self.bus.publish("command", Command("ramp_electrolyzer", drifted))

    def tune_models(self):
        self.bus.publish("command", Command("retrain_thresholds"))

    def reconcile_inventories(self):
        self.bus.publish("command", Command("reconcile_inventories"))

    # GUI signals with rogue drift
    def emit_gui(self):
        g = {
            "state": self.state,
            "storm_risk": self.rf.storm_risk,
            "grid_volatility": self.rf.grid_volatility,
            "stress": self.rf.stress_score,
            "rogue_drift": random.uniform(-0.1, 0.1),
            "lightning_proximity_km": self.sf.lightning_proximity_km,
            "strike_density_per_min": self.sf.strike_density_per_min,
            "wind_gust_ms": self.sf.wind_gust_ms,
            "h2_soc_pct": self.pf.h2_soc_pct,
            "battery_soc_pct": self.pf.battery_soc_pct,
        }
        self.bus.publish("gui.signal", GuiSignal(ts=time.time(), topic="dashboard", data=g))

# ==========
# Actuators
# ==========

class Actuators:
    def __init__(self, bus: EventBus):
        bus.subscribe("command", self.on_command)

    def on_command(self, cmd: Command):
        print(f"[act] {cmd.name} {cmd.args}")

# ===========
# GUI bridge
# ===========

class GuiBridge:
    def __init__(self, bus: EventBus):
        bus.subscribe("gui.signal", self.on_signal)
        bus.subscribe("controller.event", self.on_controller_event)

    def on_signal(self, sig: GuiSignal):
        d = sig.data
        print(f"[gui] state={d['state']} risk={d['storm_risk']:.2f} vol={d['grid_volatility']:.2f} stress={d['stress']:.2f} "
              f"rogue={d['rogue_drift']:.2f} prox={d['lightning_proximity_km']:.1f}km strikes={d['strike_density_per_min']:.1f}/min gust={d['wind_gust_ms']:.1f} "
              f"H2_SOC={d['h2_soc_pct']:.1f}% Batt_SOC={d['battery_soc_pct']:.1f}%")

    def on_controller_event(self, evt):
        print(f"[gui] transition -> {evt['to']}")

# ==========
# Main
# ==========

def main():
    bus = EventBus()
    storm = StormSensors(bus, interval=0.75)
    process = ProcessSensors(bus, interval=0.75)
    ctrl = Controller(bus)
    acts = Actuators(bus)
    gui = GuiBridge(bus)

    storm.start()
    process.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        storm.stop()
        process.stop()
        print("\n[system] stopped.")

if __name__ == "__main__":
    main()


    
    
    


    

