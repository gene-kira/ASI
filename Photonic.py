# ============================================================
# Autoloader: install/check required libraries and versions
# ============================================================
import importlib
import subprocess
import sys
import os
import json
from datetime import datetime
import time

REQUIRED_LIBS = {
    "numpy": "1.20.0",
    "matplotlib": "3.5.0",
    "PySide6": "6.4.0"
}

def ensure_lib(name, min_version=None):
    try:
        mod = importlib.import_module(name)
        if min_version:
            def parse_v(v):
                parts = []
                for x in v.split("."):
                    num = ''.join(ch for ch in x if ch.isdigit())
                    parts.append(int(num) if num else 0)
                parts = parts[:3] + [0]*(3-len(parts))
                return tuple(parts)
            cur = parse_v(getattr(mod, "__version__", "0.0.0"))
            req = parse_v(min_version)
            if cur < req:
                print(f"[UPGRADE] {name} {getattr(mod,'__version__','')} < {min_version}. Upgrading...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{name}>={min_version}"])
                mod = importlib.import_module(name)
                print(f"[OK] {name} upgraded to {getattr(mod,'__version__','')}")
        else:
            print(f"[OK] {name} loaded")
        return mod
    except ImportError:
        print(f"[MISSING] {name} not found. Installing...")
        pkg_spec = f"{name}>={min_version}" if min_version else name
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_spec])
        mod = importlib.import_module(name)
        print(f"[INSTALLED] {name} {getattr(mod, '__version__', '')} installed")
        return mod

np = ensure_lib("numpy", REQUIRED_LIBS["numpy"])
mpl = ensure_lib("matplotlib", REQUIRED_LIBS["matplotlib"])
import matplotlib.pyplot as plt

# Try GUI lib; allow headless fallback
GUI_AVAILABLE = True
try:
    PySide6 = ensure_lib("PySide6", REQUIRED_LIBS["PySide6"])
    from PySide6.QtWidgets import (
        QApplication, QWidget, QGridLayout, QLabel, QDoubleSpinBox,
        QPushButton, QHBoxLayout, QCheckBox
    )
    from PySide6.QtCore import QTimer
except Exception as e:
    print(f"[WARN] GUI not available ({e}). Running headless.")
    GUI_AVAILABLE = False

# ============================================================
# Paths and persistence helpers
# ============================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CFG_PATH = os.path.join(BASE_DIR, "photonic_config.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_CFG = {
    "mode": "simulation",           # "simulation" or "real_world"
    "n": 8,
    "channels": 4,
    "layers": 4,
    "T": 2048,
    "fs": 20e9,
    "carriers": {"f0": 2e9, "delta": 0.5e9},
    "impairments": {"loss_db": 1.0, "phase_noise": 0.02, "beta2": 1e-26, "length": 10.0},
    "rng_seed": 42,
    "mesh_seed": 7,
    "watchdog_interval_ms": 2000,
    "enable_gui": True,
    "autonomous_interval_s": 3.0
}

def load_config(default_cfg):
    if os.path.exists(CFG_PATH):
        with open(CFG_PATH, "r") as f:
            try:
                cfg = json.load(f)
                print(f"[CFG] Loaded from {CFG_PATH}")
                return {**default_cfg, **cfg}
            except Exception as e:
                print(f"[CFG] Failed to parse config, using defaults: {e}")
    with open(CFG_PATH, "w") as f:
        json.dump(default_cfg, f, indent=2)
    print(f"[CFG] Created default config at {CFG_PATH}")
    return default_cfg

def save_config(cfg):
    with open(CFG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"[CFG] Saved config to {CFG_PATH}")

# Simple rotating telemetry logger
class TelemetryLogger:
    def __init__(self, prefix="telemetry", max_lines=5000):
        self.path = os.path.join(LOG_DIR, f"{prefix}.log")
        self.max_lines = max_lines
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write("# Telemetry log\n")

    def write(self, message):
        stamp = datetime.utcnow().isoformat()
        line = f"{stamp} | {message}\n"
        with open(self.path, "a") as f:
            f.write(line)
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
            if len(lines) > self.max_lines:
                backup = self.path.replace(".log", f"_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.log")
                os.rename(self.path, backup)
                self._ensure_file()
                print(f"[LOG] Rotated telemetry to {backup}")
        except Exception as e:
            print(f"[LOG] Rotation failed: {e}")

telemetry = TelemetryLogger()

# ============================================================
# Photonic primitives and core (simulation layer)
# ============================================================
def mzi(theta, phi):
    c = np.cos(theta)
    s = np.sin(theta)
    U = np.array([[c, 1j*s],
                  [1j*s, c]], dtype=np.complex128)
    P = np.diag([np.exp(1j*phi), 1.0])
    return P @ U

def lossy(U, alpha_db):
    alpha = 10 ** (-alpha_db / 20.0)
    return alpha * U

def add_phase_noise(U, sigma_rad, rng=None):
    rng = rng or np.random.default_rng()
    jitter = np.exp(1j * rng.normal(0, sigma_rad, U.shape))
    return U * jitter

def clements_mesh(n, thetas, phis):
    U = np.eye(n, dtype=np.complex128)
    num_layers = len(thetas)
    for layer in range(num_layers):
        layer_U = np.eye(n, dtype=np.complex128)
        offset = 0 if layer % 2 == 0 else 1
        for i, (theta, phi) in enumerate(zip(thetas[layer], phis[layer])):
            a = offset + 2*i
            if a + 1 >= n:
                continue
            block = mzi(theta, phi)
            layer_U[a:a+2, a:a+2] = block @ layer_U[a:a+2, a:a+2]
        U = layer_U @ U
    return U

def random_mesh_params(n, layers, seed=None):
    rng = np.random.default_rng(seed)
    thetas = [rng.uniform(0, np.pi/2, size=(n//2,)).tolist() for _ in range(layers)]
    phis   = [rng.uniform(0, 2*np.pi, size=(n//2,)).tolist() for _ in range(layers)]
    return thetas, phis

def apply_dispersion(signal_fft, freqs, beta2, length):
    omega = 2*np.pi*freqs
    phase = np.exp(-1j * 0.5 * beta2 * omega**2 * length)
    return signal_fft * phase

class WDMPhotonicCoreSim:
    def __init__(self, n, channels, layers=2, impairments=None, seed=None):
        self.n = n
        self.channels = channels
        self.layers = layers
        self.impairments = impairments or {}
        self.rng = np.random.default_rng(seed)

        self.mesh_U = []
        for _ in range(channels):
            thetas, phis = random_mesh_params(n, layers, seed=self.rng.integers(1e9))
            U = clements_mesh(n, thetas, phis)
            if 'loss_db' in self.impairments:
                U = lossy(U, self.impairments['loss_db'])
            if 'phase_noise' in self.impairments:
                U = add_phase_noise(U, self.impairments['phase_noise'], rng=self.rng)
            self.mesh_U.append(U)

    def compute(self, X_time, sample_rate_hz):
        outputs = []
        T = X_time[0].shape[1]
        freqs = np.fft.fftfreq(T, d=1.0/sample_rate_hz)
        for ch in range(self.channels):
            U = self.mesh_U[ch]
            Y = U @ X_time[ch]
            if 'beta2' in self.impairments and 'length' in self.impairments:
                Y_fft = np.fft.fft(Y, axis=1)
                Y_fft = apply_dispersion(Y_fft, freqs, self.impairments['beta2'], self.impairments['length'])
                Y = np.fft.ifft(Y_fft, axis=1)
            outputs.append(Y)
        return outputs

# ============================================================
# Hardware driver stubs (real-world hooks)
# ============================================================
class HardwareInterface:
    """
    Replace these methods with real drivers to your hardware.
    Integrate with DAQ/ADC/DAC, optical power meters, phase shifters, etc.
    """
    def __init__(self, n, channels):
        self.n = n
        self.channels = channels
        # Example: placeholders for device handles
        self.devices = {"phase_shifters": None, "power_meters": None, "daq": None}

    def read_input_signals(self, T, fs):
        """
        Acquire complex signals from hardware for each channel.
        For now, generate placeholders to prove pipeline; replace with ADC reads.
        """
        rng = np.random.default_rng(123)
        X = []
        t = np.arange(T) / fs
        for ch in range(self.channels):
            # Simulate I/Q capture (replace with hardware samples)
            I = rng.standard_normal((self.n, T))
            Q = rng.standard_normal((self.n, T))
            X.append((I + 1j*Q) / np.sqrt(2))
        return X

    def measure_output_energy(self, Y):
        """
        Use optical/electrical power meters or device-reported metrics.
        Here, compute mean |Y|^2; replace with instrument queries.
        """
        return [np.mean(np.abs(Y[ch])**2) for ch in range(len(Y))]

    def get_phase_shifter_states(self):
        """
        Query hardware phase shifter values; return list per channel.
        """
        return [{"channel": ch, "phases": [0.0]*self.n} for ch in range(self.channels)]

    def set_phase_shifter(self, channel, index, value):
        """
        Adjust a specific phase shifter (thermal/electro-optic) in hardware.
        """
        telemetry.write(f"[HW] set_phase_shifter ch={channel} idx={index} val={value}")

    def calibrate(self, target=None):
        """
        Run a hardware calibration routine: align phases, equalize power, etc.
        """
        telemetry.write("[HW] calibration started")
        # Placeholder: add your routine here
        time.sleep(0.5)
        telemetry.write("[HW] calibration done")
        return True

class WDMPhotonicCoreHW:
    """
    Real-world mode: compute() represents applying current hardware transform.
    Mesh parameters are not simulated; they map to hardware state.
    """
    def __init__(self, n, channels, hardware: HardwareInterface, impairments=None):
        self.n = n
        self.channels = channels
        self.hardware = hardware
        self.impairments = impairments or {}

    def compute(self, X_time, sample_rate_hz):
        """
        In real hardware, you would send X_time through the optical/electrical path
        and capture outputs. Here, we placeholder a pass-through with minor noise.
        """
        outputs = []
        rng = np.random.default_rng(99)
        for ch in range(self.channels):
            noise = (rng.standard_normal(X_time[ch].shape) + 1j * rng.standard_normal(X_time[ch].shape)) * 1e-3
            Y = X_time[ch] + noise  # Replace with hardware capture path
            outputs.append(Y)
        return outputs

# ============================================================
# Generators (simulation mode only)
# ============================================================
def generate_signals(n, channels, T, fs, f0, delta, seed=None):
    rng = np.random.default_rng(seed)
    X = []
    t = np.arange(T) / fs
    for ch in range(channels):
        base = (rng.standard_normal((n, T)) + 1j * rng.standard_normal((n, T))) / np.sqrt(2)
        carrier = np.exp(1j * 2*np.pi * (f0 + delta*ch) * t)
        X.append(base * carrier)
    return X

# ============================================================
# Watchdog and autonomous loop
# ============================================================
class Watchdog:
    def __init__(self, compute_fn, measure_fn, interval_ms=2000):
        self.compute_fn = compute_fn
        self.measure_fn = measure_fn
        self.interval_ms = interval_ms
        self.last_energy = None
        self.timer = None

    def start_gui(self, X, fs):
        if not GUI_AVAILABLE:
            return
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.check(X, fs))
        self.timer.start(self.interval_ms)
        telemetry.write(f"[WATCHDOG] started interval={self.interval_ms}ms")

    def check(self, X, fs):
        try:
            Y = self.compute_fn(X, fs)
            energies_out = self.measure_fn(Y)
            if self.last_energy is not None:
                drift = np.mean([abs(e - p) for e, p in zip(energies_out, self.last_energy)])
                telemetry.write(f"[WATCHDOG] energies={energies_out} drift={drift:.6f}")
            self.last_energy = energies_out
        except Exception as e:
            telemetry.write(f"[WATCHDOG][ERROR] {e}")

def autonomous_run(cfg, compute_fn, input_provider, measure_fn):
    interval = cfg.get("autonomous_interval_s", 3.0)
    fs = cfg["fs"]; T = cfg["T"]
    while True:
        X = input_provider(T, fs)
        Y = compute_fn(X, fs)
        energies = measure_fn(Y)
        drift = np.std(energies)
        telemetry.write(f"[AUTO] energies={['%.6f'%e for e in energies]} drift={drift:.6f}")
        time.sleep(interval)

# ============================================================
# Minimal GUI indicator panel
# ============================================================
class MinimalPanel(QWidget):
    def __init__(self, cfg, mode, compute_fn, input_provider, measure_fn):
        super().__init__()
        self.cfg = cfg
        self.mode = mode
        self.compute_fn = compute_fn
        self.input_provider = input_provider
        self.measure_fn = measure_fn

        self.setWindowTitle(f"Photonic Bridge ({mode})")
        layout = QGridLayout(self)

        # Status label
        self.lbl_status = QLabel("Status: Initializing")
        self.lbl_status.setStyleSheet("color: orange; font-weight: bold;")
        layout.addWidget(self.lbl_status, 0, 0, 1, 2)

        # Impairment controls (only meaningful in simulation)
        layout.addWidget(QLabel("Loss (dB)"), 1, 0)
        self.sp_loss = QDoubleSpinBox(); self.sp_loss.setRange(0.0, 10.0); self.sp_loss.setSingleStep(0.1); self.sp_loss.setValue(cfg["impairments"]["loss_db"])
        layout.addWidget(self.sp_loss, 1, 1)

        layout.addWidget(QLabel("Phase noise (rad)"), 2, 0)
        self.sp_noise = QDoubleSpinBox(); self.sp_noise.setRange(0.0, 0.5); self.sp_noise.setSingleStep(0.005); self.sp_noise.setValue(cfg["impairments"]["phase_noise"])
        layout.addWidget(self.sp_noise, 2, 1)

        layout.addWidget(QLabel("Beta2 (s^2/m)"), 3, 0)
        self.sp_beta2 = QDoubleSpinBox(); self.sp_beta2.setRange(0.0, 5e-26); self.sp_beta2.setSingleStep(1e-27); self.sp_beta2.setDecimals(12); self.sp_beta2.setValue(cfg["impairments"]["beta2"])
        layout.addWidget(self.sp_beta2, 3, 1)

        layout.addWidget(QLabel("Length (m)"), 4, 0)
        self.sp_length = QDoubleSpinBox(); self.sp_length.setRange(0.0, 100.0); self.sp_length.setSingleStep(1.0); self.sp_length.setValue(cfg["impairments"]["length"])
        layout.addWidget(self.sp_length, 4, 1)

        # Buttons
        btns = QHBoxLayout()
        self.btn_apply = QPushButton("Apply/Recompute")
        self.btn_reset = QPushButton("Reset")
        self.btn_snapshot = QPushButton("Snapshot")
        btns.addWidget(self.btn_apply); btns.addWidget(self.btn_reset); btns.addWidget(self.btn_snapshot)
        layout.addLayout(btns, 5, 0, 1, 2)

        # Headless plot toggle (quick view)
        self.cb_headless = QCheckBox("Headless (skip plots)")
        self.cb_headless.setChecked(True)
        layout.addWidget(self.cb_headless, 6, 0, 1, 2)

        # Timed updates (simulate or poll hardware)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(self.cfg.get("watchdog_interval_ms", 2000))

        # Hooks
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_snapshot.clicked.connect(self.on_snapshot)

        # Initial snapshot
        self.on_snapshot()

    def on_apply(self):
        # Update config impairments (simulation mode)
        self.cfg["impairments"]["loss_db"] = float(self.sp_loss.value())
        self.cfg["impairments"]["phase_noise"] = float(self.sp_noise.value())
        self.cfg["impairments"]["beta2"] = float(self.sp_beta2.value())
        self.cfg["impairments"]["length"] = float(self.sp_length.value())
        save_config(self.cfg)
        telemetry.write(f"[GUI] Apply impairments {self.cfg['impairments']}")
        self.on_snapshot()

    def on_reset(self):
        self.sp_loss.setValue(0.0)
        self.sp_noise.setValue(0.0)
        self.sp_beta2.setValue(0.0)
        self.sp_length.setValue(0.0)
        self.on_apply()

    def on_snapshot(self):
        # Acquire and compute once
        X = self.input_provider(self.cfg["T"], self.cfg["fs"])
        Y = self.compute_fn(X, self.cfg["fs"])
        energies = self.measure_fn(Y)
        drift = float(np.std(energies))
        telemetry.write(f"[GUI] snapshot energies={['%.6f'%e for e in energies]} drift={drift:.6f}")
        self.set_health(drift, calibrated=True)

        if not self.cb_headless.isChecked():
            # Quick plots
            T = X[0].shape[1]
            t_ns = np.arange(T) / self.cfg["fs"] * 1e9
            freqs = np.fft.fftfreq(T, d=1.0/self.cfg["fs"]) / 1e9
            colors = plt.cm.tab10(np.linspace(0,1,len(X)))
            fig, (ax_t, ax_f) = plt.subplots(2, 1, figsize=(10,7))
            ax_t.set_title("Time-domain amplitude (component 0)")
            ax_t.set_xlabel("Time (ns)"); ax_t.set_ylabel("|x| / |y|")
            for ch in range(len(X)):
                ax_t.plot(t_ns, np.abs(X[ch][0]), color=colors[ch], alpha=0.5, label=f"X ch{ch}")
                ax_t.plot(t_ns, np.abs(Y[ch][0]), color=colors[ch], linewidth=2, label=f"Y ch{ch}")
            ax_t.legend(ncol=2, fontsize=9)
            ax_f.set_title("Frequency magnitude (component 0)")
            ax_f.set_xlabel("Frequency (GHz)"); ax_f.set_ylabel("|FFT|")
            for ch in range(len(X)):
                FX = np.fft.fft(X[ch][0])
                FY = np.fft.fft(Y[ch][0])
                ax_f.plot(freqs, np.abs(FX), color=colors[ch], alpha=0.5, label=f"X ch{ch}")
                ax_f.plot(freqs, np.abs(FY), color=colors[ch], linewidth=2, label=f"Y ch{ch}")
            ax_f.legend(ncol=2, fontsize=9)
            plt.tight_layout()
            plt.show()

    def update_status(self):
        # Periodic snapshot to show health
        self.on_snapshot()

    def set_health(self, drift, calibrated):
        # Green: stable; Orange: mild drift; Red: recalibration recommended
        if drift < 0.01 and calibrated:
            self.lbl_status.setText("Status: Stable")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        elif drift < 0.05:
            self.lbl_status.setText(f"Status: Drift Detected ({drift:.4f})")
            self.lbl_status.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.lbl_status.setText(f"Status: Recalibration Needed ({drift:.4f})")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")

# ============================================================
# Entry point: build cores, signals/hardware, GUI/headless
# ============================================================
def main():
    cfg = load_config(DEFAULT_CFG)
    mode = cfg.get("mode", "simulation")
    n = cfg["n"]; channels = cfg["channels"]; layers = cfg["layers"]
    T = cfg["T"]; fs = cfg["fs"]
    f0 = cfg["carriers"]["f0"]; delta = cfg["carriers"]["delta"]
    impair = cfg["impairments"]

    # Build runtime based on mode
    if mode == "real_world":
        hw = HardwareInterface(n, channels)
        core_hw = WDMPhotonicCoreHW(n, channels, hardware=hw, impairments=impair)

        def input_provider(T, fs):
            return hw.read_input_signals(T, fs)

        def compute_fn(X, fs):
            return core_hw.compute(X, sample_rate_hz=fs)

        def measure_fn(Y):
            return hw.measure_output_energy(Y)

        telemetry.write("[Startup] Real-world mode enabled")
    else:
        core_sim = WDMPhotonicCoreSim(n, channels, layers=layers, impairments=impair, seed=cfg["mesh_seed"])

        def input_provider(T, fs):
            return generate_signals(n, channels, T, fs, f0, delta, seed=cfg["rng_seed"])

        def compute_fn(X, fs):
            return core_sim.compute(X, sample_rate_hz=fs)

        def measure_fn(Y):
            return [np.mean(np.abs(Y[ch])**2) for ch in range(len(Y))]

        telemetry.write("[Startup] Simulation mode enabled")

    # Initial telemetry snapshot
    X0 = input_provider(T, fs)
    Y0 = compute_fn(X0, fs)
    for ch in range(channels):
        energy_in = float(np.mean(np.abs(X0[ch])**2))
        energy_out = float(np.mean(np.abs(Y0[ch])**2))
        telemetry.write(f"[Startup] ch={ch} Ein={energy_in:.6f} Eout={energy_out:.6f}")

    # Watchdog
    watchdog = Watchdog(compute_fn, measure_fn, interval_ms=cfg.get("watchdog_interval_ms", 2000))

    # Decide runtime mode: GUI or autonomous headless
    use_gui = GUI_AVAILABLE and cfg.get("enable_gui", True)
    if use_gui:
        app = QApplication(sys.argv)
        panel = MinimalPanel(cfg, mode, compute_fn, input_provider, measure_fn)
        panel.resize(520, 260)
        panel.show()
        watchdog.start_gui(input_provider(T, fs), fs)
        sys.exit(app.exec())
    else:
        print("[HEADLESS] GUI disabled/unavailable. Running autonomous loop.")
        autonomous_run(cfg, compute_fn, input_provider, measure_fn)

if __name__ == "__main__":
    main()

