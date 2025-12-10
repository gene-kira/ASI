# ============================================================
# Autoloader: install missing libraries and enforce versions
# ============================================================
import importlib
import subprocess
import sys
import os
import json
import time
from datetime import datetime

REQUIRED_LIBS = {
    "numpy": "1.20.0",
    "matplotlib": "3.5.0",
}

def ensure_lib(name, min_version=None):
    try:
        mod = importlib.import_module(name)
        if min_version:
            def parse_v(v):
                return tuple(int(x) for x in v.split(".") if x.isdigit())
            cur = parse_v(getattr(mod, "__version__", "0.0.0"))
            req = parse_v(min_version)
            if cur < req:
                print(f"[UPGRADE] {name} {getattr(mod, '__version__','?')} < {min_version}. Upgrading...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{name}>={min_version}"])
                mod = importlib.import_module(name)
                print(f"[OK] {name} upgraded to {getattr(mod,'__version__','?')}")
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
from matplotlib.widgets import Slider, Button

# ============================================================
# Paths and persistence
# ============================================================
APP_DIR = os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
CFG_PATH = os.path.join(APP_DIR, "photonic_config.json")
LOG_PATH = os.path.join(APP_DIR, "photonic_telemetry.csv")

def load_config(default_cfg):
    if os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH, "r") as f:
                cfg = json.load(f)
            print(f"[CFG] Loaded config from {CFG_PATH}")
            return {**default_cfg, **cfg}
        except Exception as e:
            print(f"[CFG] Failed to load config: {e}. Using defaults.")
    return default_cfg

def save_config(cfg):
    try:
        with open(CFG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"[CFG] Saved config to {CFG_PATH}")
    except Exception as e:
        print(f"[CFG] Failed to save config: {e}")

def append_log(row_dict):
    header_needed = not os.path.exists(LOG_PATH)
    try:
        with open(LOG_PATH, "a") as f:
            if header_needed:
                f.write(",".join(row_dict.keys()) + "\n")
            f.write(",".join(str(v) for v in row_dict.values()) + "\n")
    except Exception as e:
        print(f"[LOG] Failed to append telemetry: {e}")

# ============================================================
# Photonic primitives: MZI, loss, noise
# ============================================================
def mzi(theta, phi):
    """
    Mach–Zehnder interferometer ideal 2x2 transfer.
    theta: coupling control
    phi: output phase shift on one arm
    """
    c = np.cos(theta)
    s = np.sin(theta)
    U = np.array([[c, 1j*s],
                  [1j*s, c]], dtype=np.complex128)
    P = np.diag([np.exp(1j*phi), 1.0])
    return P @ U

def lossy(U, alpha_db):
    """Apply uniform loss (dB) to matrix U."""
    alpha = 10 ** (-alpha_db / 20.0)
    return alpha * U

def add_phase_noise(U, sigma_rad, rng=None):
    """Element-wise complex phase jitter."""
    rng = rng or np.random.default_rng()
    jitter = np.exp(1j * rng.normal(0, sigma_rad, U.shape))
    return U * jitter

# ============================================================
# Mesh constructors (Clements-style layering)
# ============================================================
def clements_mesh(n, thetas, phis):
    """
    Build NxN transfer via layered MZI mesh.
    thetas, phis: lists per layer [layer][mzi_index]
    """
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

# ============================================================
# Dispersion model
# ============================================================
def apply_dispersion(signal_fft, freqs, beta2, length):
    """
    Quadratic phase dispersion: exp(-j * 0.5 * beta2 * omega^2 * L)
    beta2: s^2/m
    length: m
    """
    omega = 2*np.pi*freqs
    phase = np.exp(-1j * 0.5 * beta2 * omega**2 * length)
    return signal_fft * phase

# ============================================================
# WDM Photonic Core
# ============================================================
class WDMPhotonicCore:
    def __init__(self, n, channels, layers=2, impairments=None, seed=None):
        """
        n: vector dimension per channel
        channels: number of wavelengths
        layers: mesh depth
        impairments: dict {'loss_db','phase_noise','beta2','length'}
        """
        self.n = n
        self.channels = channels
        self.layers = layers
        self.impairments = impairments or {}
        self.rng = np.random.default_rng(seed)

        self.mesh_U = []
        for ch in range(channels):
            thetas, phis = random_mesh_params(n, layers, seed=self.rng.integers(1e9))
            U = clements_mesh(n, thetas, phis)
            if 'loss_db' in self.impairments:
                U = lossy(U, self.impairments['loss_db'])
            if 'phase_noise' in self.impairments:
                U = add_phase_noise(U, self.impairments['phase_noise'], rng=self.rng)
            self.mesh_U.append(U)

    def compute(self, X_time, sample_rate_hz):
        """
        X_time: list per channel, each shape (n, T) complex
        sample_rate_hz: sampling rate (Hz) for dispersion model
        Returns: list of outputs per channel, shape (n, T)
        """
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

    # -----------------------
    # Calibration interface
    # -----------------------
    def set_target_matrix(self, W_per_channel):
        """
        Calibrate each channel mesh to approximate a given target matrix.
        Method: polar decomposition via SVD -> nearest unitary Q = U @ V^H.
        Applies impairments after calibration.
        W_per_channel: list of (n x n) complex matrices
        """
        calibrated = []
        for ch, W in enumerate(W_per_channel):
            # SVD-based polar decomposition: W = U S V^H -> Q = U V^H (unitary)
            U_svd, _, Vh = np.linalg.svd(W)
            Q = U_svd @ Vh
            # Apply current impairments (loss/noise)
            if 'loss_db' in self.impairments:
                Q = lossy(Q, self.impairments['loss_db'])
            if 'phase_noise' in self.impairments and self.impairments['phase_noise'] > 0:
                Q = add_phase_noise(Q, self.impairments['phase_noise'], rng=self.rng)
            calibrated.append(Q)
        self.mesh_U = calibrated

# ============================================================
# Configuration (defaults, loaded from disk if present)
# ============================================================
DEFAULT_CFG = {
    "n": 8,                # vector dimension per wavelength
    "channels": 4,         # number of WDM channels
    "layers": 4,           # mesh depth (more layers -> richer transforms)
    "T": 2048,             # time samples (increase for finer spectra)
    "fs": 20e9,            # sample rate (Hz) as electrical proxy
    "carriers": {          # carrier frequencies per channel (Hz)
        "f0": 2e9,
        "delta": 0.5e9
    },
    "impairments": {
        "loss_db": 1.0,      # uniform loss (dB)
        "phase_noise": 0.02, # radians std
        "beta2": 1e-26,      # s^2/m
        "length": 10.0       # m
    },
    "rng_seed": 42,
    "mesh_seed": 7,
    "watchdog": {
        "enabled": True,
        "interval_s": 3.0,
        "drift_threshold": 0.05  # relative energy drift to trigger recompute
    }
}
CFG = load_config(DEFAULT_CFG)

# ============================================================
# Signal generation
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
# Visualization dashboard
# ============================================================
class PhotonicDashboard:
    def __init__(self, core, X, fs, cfg_ref):
        self.core = core
        self.X = X
        self.fs = fs
        self.cfg_ref = cfg_ref
        self.channels = len(X)
        self.n = X[0].shape[0]
        self.T = X[0].shape[1]
        self.last_energies_out = None
        self.last_recompute_time = time.time()

        # Initial compute
        self.Y = core.compute(X, sample_rate_hz=fs)

        # Precompute time and freq axes
        self.t_ns = np.arange(self.T) / fs * 1e9
        self.freqs = np.fft.fftfreq(self.T, d=1.0/fs) / 1e9  # GHz

        # Matplotlib setup
        self.fig = plt.figure(figsize=(14, 9))
        gs = self.fig.add_gridspec(3, 3, height_ratios=[3,3,1])

        # Time-domain (one component per channel)
        self.ax_time = self.fig.add_subplot(gs[0, :2])
        self.ax_time.set_title("Time-domain amplitude (component 0 of each channel)")
        self.ax_time.set_xlabel("Time (ns)")
        self.ax_time.set_ylabel("|x| and |y|")
        self.lines_x = []
        self.lines_y = []
        colors = plt.cm.tab10(np.linspace(0,1,self.channels))
        for ch in range(self.channels):
            lx, = self.ax_time.plot(self.t_ns, np.abs(self.X[ch][0]), color=colors[ch], alpha=0.5, label=f"X ch{ch}")
            ly, = self.ax_time.plot(self.t_ns, np.abs(self.Y[ch][0]), color=colors[ch], linewidth=2, label=f"Y ch{ch}")
            self.lines_x.append(lx)
            self.lines_y.append(ly)
        self.ax_time.legend(ncol=2, fontsize=9)

        # Frequency-domain magnitude (component 0)
        self.ax_freq = self.fig.add_subplot(gs[1, :2])
        self.ax_freq.set_title("Frequency magnitude (component 0)")
        self.ax_freq.set_xlabel("Frequency (GHz)")
        self.ax_freq.set_ylabel("|FFT|")
        self.lines_fx = []
        self.lines_fy = []
        for ch in range(self.channels):
            FX = np.fft.fft(self.X[ch][0])
            FY = np.fft.fft(self.Y[ch][0])
            lfx, = self.ax_freq.plot(self.freqs, np.abs(FX), color=colors[ch], alpha=0.5, label=f"X ch{ch}")
            lfy, = self.ax_freq.plot(self.freqs, np.abs(FY), color=colors[ch], linewidth=2, label=f"Y ch{ch}")
            self.lines_fx.append(lfx)
            self.lines_fy.append(lfy)
        self.ax_freq.legend(ncol=2, fontsize=9)

        # Energy bars
        self.ax_energy = self.fig.add_subplot(gs[2, 0])
        self.ax_energy.set_title("Channel energy (mean |.|^2)")
        self.ax_energy.set_ylabel("Energy")
        self.ax_energy.set_xticks(range(self.channels))
        self.ax_energy.set_xlabel("Channel")
        self.bars_in = None
        self.bars_out = None
        self.update_energy_bars()

        # Mesh phase overlay (arg of U for channel 0)
        self.ax_phase = self.fig.add_subplot(gs[0, 2])
        self.ax_phase.set_title("Mesh phase overlay (arg(U) ch0)")
        self.phase_img = None
        self.update_phase_overlay(channel=0)

        # Control sliders
        self.ax_controls = self.fig.add_subplot(gs[2, 1])
        self.ax_controls.set_axis_off()
        axcolor = 'lightgoldenrodyellow'
        slider_height = 0.03

        self.ax_loss   = plt.axes([0.55, 0.18, 0.40, slider_height], facecolor=axcolor)
        self.ax_noise  = plt.axes([0.55, 0.14, 0.40, slider_height], facecolor=axcolor)
        self.ax_beta2  = plt.axes([0.55, 0.10, 0.40, slider_height], facecolor=axcolor)
        self.ax_length = plt.axes([0.55, 0.06, 0.40, slider_height], facecolor=axcolor)

        impair = self.core.impairments
        self.sl_loss   = Slider(self.ax_loss,   'Loss (dB)',        0.0, 6.0,   valinit=impair.get('loss_db', 0.0),     valstep=0.1)
        self.sl_noise  = Slider(self.ax_noise,  'Phase noise (rad)',0.0, 0.2,   valinit=impair.get('phase_noise', 0.0), valstep=0.005)
        self.sl_beta2  = Slider(self.ax_beta2,  'Beta2 (s^2/m)',    0.0, 5e-26, valinit=impair.get('beta2', 0.0),       valstep=1e-27)
        self.sl_length = Slider(self.ax_length, 'Length (m)',       0.0, 50.0,  valinit=impair.get('length', 0.0),      valstep=1.0)

        # Buttons
        self.ax_btn_apply   = plt.axes([0.55, 0.22, 0.15, 0.04])
        self.ax_btn_reset   = plt.axes([0.73, 0.22, 0.15, 0.04])
        self.ax_btn_calib   = plt.axes([0.55, 0.26, 0.33, 0.04])

        self.btn_apply = Button(self.ax_btn_apply, 'Apply/Recompute')
        self.btn_reset = Button(self.ax_btn_reset, 'Reset Impairments')
        self.btn_calib = Button(self.ax_btn_calib, 'Calibrate to random target')

        # Status text
        self.status_text = self.fig.text(0.55, 0.92, self.status_line(), fontsize=9, family='monospace')

        # Bind events
        self.btn_apply.on_clicked(self.on_apply)
        self.btn_reset.on_clicked(self.on_reset)
        self.btn_calib.on_clicked(self.on_calibrate)

        # Watchdog timer (basic)
        if self.cfg_ref.get("watchdog", {}).get("enabled", False):
            self.fig.canvas.mpl_connect('draw_event', self.on_watchdog_tick)

        plt.tight_layout()

    def status_line(self):
        imp = self.core.impairments
        return (f"loss_db={imp.get('loss_db',0):.2f} | "
                f"phase_noise={imp.get('phase_noise',0):.3f} rad | "
                f"beta2={imp.get('beta2',0):.2e} s^2/m | "
                f"length={imp.get('length',0):.1f} m")

    def update_energy_bars(self):
        energies_in = [np.mean(np.abs(self.X[ch])**2) for ch in range(self.channels)]
        energies_out = [np.mean(np.abs(self.Y[ch])**2) for ch in range(self.channels)]
        x = np.arange(self.channels)
        if self.bars_in is None:
            width = 0.35
            self.bars_in = self.ax_energy.bar(x - width/2, energies_in, width, label='Input')
            self.bars_out = self.ax_energy.bar(x + width/2, energies_out, width, label='Output')
            self.ax_energy.legend()
        else:
            for bi, e in zip(self.bars_in, energies_in):
                bi.set_height(e)
            for bo, e in zip(self.bars_out, energies_out):
                bo.set_height(e)
        self.ax_energy.set_ylim(0, max(max(energies_in), max(energies_out)) * 1.2)
        self.last_energies_out = energies_out

    def update_phase_overlay(self, channel=0):
        U = self.core.mesh_U[channel]
        phase = np.angle(U)
        if self.phase_img is None:
            self.phase_img = self.ax_phase.imshow(phase, cmap='twilight', aspect='auto')
            self.fig.colorbar(self.phase_img, ax=self.ax_phase, fraction=0.046, pad=0.04)
        else:
            self.phase_img.set_data(phase)
        self.ax_phase.set_xlabel("Col")
        self.ax_phase.set_ylabel("Row")

    def redraw_plots(self):
        # Time-domain component 0
        for ch in range(self.channels):
            self.lines_x[ch].set_ydata(np.abs(self.X[ch][0]))
            self.lines_y[ch].set_ydata(np.abs(self.Y[ch][0]))
        self.ax_time.relim()
        self.ax_time.autoscale_view()

        # Frequency-domain component 0
        for ch in range(self.channels):
            FX = np.fft.fft(self.X[ch][0])
            FY = np.fft.fft(self.Y[ch][0])
            self.lines_fx[ch].set_ydata(np.abs(FX))
            self.lines_fy[ch].set_ydata(np.abs(FY))
        self.ax_freq.relim()
        self.ax_freq.autoscale_view()

        self.update_energy_bars()
        self.update_phase_overlay(channel=0)
        self.status_text.set_text(self.status_line())
        self.fig.canvas.draw_idle()

    def on_apply(self, event=None):
        # Update impairments from sliders
        imp = self.core.impairments
        imp['loss_db'] = float(self.sl_loss.val)
        imp['phase_noise'] = float(self.sl_noise.val)
        imp['beta2'] = float(self.sl_beta2.val)
        imp['length'] = float(self.sl_length.val)

        # Persist config
        self.cfg_ref["impairments"] = imp
        save_config(self.cfg_ref)

        # Rebuild meshes with loss/noise, then recompute
        new_meshes = []
        for U in self.core.mesh_U:
            U2 = U
            mag = np.linalg.norm(U2)
            if mag != 0:
                U2 = U2 / mag
            if imp.get('loss_db', 0.0) > 0:
                U2 = lossy(U2, imp['loss_db'])
            if imp.get('phase_noise', 0.0) > 0:
                U2 = add_phase_noise(U2, imp['phase_noise'])
            new_meshes.append(U2)
        self.core.mesh_U = new_meshes

        self.Y = self.core.compute(self.X, sample_rate_hz=self.fs)
        self.redraw_plots()
        self.last_recompute_time = time.time()

        # Telemetry log
        for ch in range(self.channels):
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "channel": ch,
                "Ein": np.mean(np.abs(self.X[ch])**2),
                "Eout": np.mean(np.abs(self.Y[ch])**2),
                "loss_db": imp.get('loss_db',0.0),
                "phase_noise": imp.get('phase_noise',0.0),
                "beta2": imp.get('beta2',0.0),
                "length": imp.get('length',0.0),
                "event": "apply"
            }
            append_log(row)

    def on_reset(self, event=None):
        # Reset sliders and impairments
        self.sl_loss.reset()
        self.sl_noise.reset()
        self.sl_beta2.reset()
        self.sl_length.reset()

        self.core.impairments['loss_db'] = 0.0
        self.core.impairments['phase_noise'] = 0.0
        self.core.impairments['beta2'] = 0.0
        self.core.impairments['length'] = 0.0

        # Persist config
        self.cfg_ref["impairments"] = self.core.impairments
        save_config(self.cfg_ref)

        # Renormalize meshes and recompute
        self.core.mesh_U = [U / (np.linalg.norm(U) if np.linalg.norm(U) != 0 else 1.0) for U in self.core.mesh_U]
        self.Y = self.core.compute(self.X, sample_rate_hz=self.fs)
        self.redraw_plots()
        self.last_recompute_time = time.time()

        # Telemetry log
        for ch in range(self.channels):
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "channel": ch,
                "Ein": np.mean(np.abs(self.X[ch])**2),
                "Eout": np.mean(np.abs(self.Y[ch])**2),
                "loss_db": 0.0,
                "phase_noise": 0.0,
                "beta2": 0.0,
                "length": 0.0,
                "event": "reset"
            }
            append_log(row)

    def on_calibrate(self, event=None):
        # Create random complex target matrices per channel and calibrate
        targets = []
        rng = np.random.default_rng(self.cfg_ref.get("rng_seed", 123))
        n = self.core.n
        for _ in range(self.channels):
            # Random complex matrix
            W = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
            targets.append(W)

        self.core.set_target_matrix(targets)
        self.Y = self.core.compute(self.X, sample_rate_hz=self.fs)
        self.redraw_plots()
        self.last_recompute_time = time.time()

        # Telemetry log (include average residual vs. target Q)
        for ch in range(self.channels):
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "channel": ch,
                "Ein": np.mean(np.abs(self.X[ch])**2),
                "Eout": np.mean(np.abs(self.Y[ch])**2),
                "loss_db": self.core.impairments.get('loss_db',0.0),
                "phase_noise": self.core.impairments.get('phase_noise',0.0),
                "beta2": self.core.impairments.get('beta2',0.0),
                "length": self.core.impairments.get('length',0.0),
                "event": "calibrate"
            }
            append_log(row)

    def on_watchdog_tick(self, event=None):
        # Simple energy-drift watchdog
        wd_cfg = self.cfg_ref.get("watchdog", {})
        if not wd_cfg.get("enabled", False):
            return
        interval = wd_cfg.get("interval_s", 3.0)
        threshold = wd_cfg.get("drift_threshold", 0.05)
        now = time.time()
        if now - self.last_recompute_time < interval:
            return

        current_out = [np.mean(np.abs(self.Y[ch])**2) for ch in range(self.channels)]
        if self.last_energies_out is None:
            self.last_energies_out = current_out
            return

        # Relative drift per channel
        drift = [0.0]*self.channels
        for i in range(self.channels):
            denom = max(self.last_energies_out[i], 1e-12)
            drift[i] = abs(current_out[i] - self.last_energies_out[i]) / denom

        if any(d > threshold for d in drift):
            print(f"[WATCHDOG] Drift {drift} exceeds threshold {threshold}. Recomputing.")
            self.on_apply()
            # Log watchdog event
            for ch in range(self.channels):
                row = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "channel": ch,
                    "Ein": np.mean(np.abs(self.X[ch])**2),
                    "Eout": np.mean(np.abs(self.Y[ch])**2),
                    "loss_db": self.core.impairments.get('loss_db',0.0),
                    "phase_noise": self.core.impairments.get('phase_noise',0.0),
                    "beta2": self.core.impairments.get('beta2',0.0),
                    "length": self.core.impairments.get('length',0.0),
                    "event": "watchdog"
                }
                append_log(row)

# ============================================================
# Main: build core, generate signals, run dashboard
# ============================================================
def main():
    n = CFG["n"]
    channels = CFG["channels"]
    layers = CFG["layers"]
    T = CFG["T"]
    fs = CFG["fs"]
    f0 = CFG["carriers"]["f0"]
    delta = CFG["carriers"]["delta"]
    impair = CFG["impairments"]

    # Generate input signals
    X = generate_signals(n, channels, T, fs, f0, delta, seed=CFG["rng_seed"])

    # Build core
    core = WDMPhotonicCore(n, channels, layers=layers, impairments=impair, seed=CFG["mesh_seed"])

    # Initial telemetry
    Y = core.compute(X, sample_rate_hz=fs)
    for ch in range(channels):
        energy_in = np.mean(np.abs(X[ch])**2)
        energy_out = np.mean(np.abs(Y[ch])**2)
        print(f"[Telemetry] Channel {ch}: Ein={energy_in:.4f}, Eout={energy_out:.4f}")
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "channel": ch,
            "Ein": energy_in,
            "Eout": energy_out,
            "loss_db": impair.get('loss_db',0.0),
            "phase_noise": impair.get('phase_noise',0.0),
            "beta2": impair.get('beta2',0.0),
            "length": impair.get('length',0.0),
            "event": "startup"
        }
        append_log(row)

    # Launch dashboard
    dash = PhotonicDashboard(core, X, fs, CFG)
    plt.show()

    print("[EXIT] Simulation closed. Config and telemetry persisted.")

if __name__ == "__main__":
    main()

