import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

# --- Atomic Simulator ---
class Atom:
    def __init__(self, symbol, protons, neutrons):
        self.symbol = symbol
        self.protons = protons
        self.neutrons = neutrons
        self.mass = self.calculate_mass()

    def calculate_mass(self):
        m_p = 1.007276
        m_n = 1.008665
        return round(self.protons * m_p + self.neutrons * m_n, 5)

    def mutate(self, delta_protons=0, delta_neutrons=0):
        self.protons += delta_protons
        self.neutrons += delta_neutrons
        self.mass = self.calculate_mass()
        return self

    def log_capsule(self):
        return {
            "Symbol": self.symbol,
            "Protons": self.protons,
            "Neutrons": self.neutrons,
            "Mass (amu)": self.mass
        }

# --- Beam Overlay ---
class BeamOverlay:
    def __init__(self):
        self.glyphs = {}

    def encode_glyph(self, atom_symbol, delta_p, delta_n):
        self.glyphs[atom_symbol] = {
            "Mutation": f"+{delta_p}p / +{delta_n}n",
            "EnergyCost": self.calculate_energy(delta_p, delta_n),
            "Script": f"[{atom_symbol}]::mutate({delta_p}p,{delta_n}n)"
        }

    def calculate_energy(self, dp, dn):
        return round((dp * 7.7 + dn * 8.5), 2)

    def get_glyph(self, atom_symbol):
        return self.glyphs.get(atom_symbol, "No glyph encoded")

# --- Containment Mesh ---
class ContainmentMesh:
    def __init__(self, threshold_mass_shift=5.0):
        self.threshold = threshold_mass_shift
        self.telemetry_log = []

    def validate_mutation(self, original_mass, mutated_mass):
        delta = abs(mutated_mass - original_mass)
        if delta > self.threshold:
            return "ABORT: Mass shift exceeds safe threshold"
        return "Mutation stable"

    def log_telemetry(self, atom_data):
        self.telemetry_log.append(atom_data)

# --- Stability Predictor ---
class StabilityPredictor:
    def is_stable(self, protons, neutrons):
        ratio = neutrons / protons
        if protons < 20:
            return 0.9 <= ratio <= 1.2
        elif protons < 83:
            return 1.3 <= ratio <= 1.5
        else:
            return 1.5 <= ratio <= 1.6

    def predict(self, symbol, protons, neutrons):
        stable = self.is_stable(protons, neutrons)
        return "Stable" if stable else "Unstable"

# --- Decay Chain ---
class DecayChain:
    def __init__(self):
        self.chains = {}

    def add_isotope(self, symbol, half_life, decay_mode):
        self.chains[symbol] = {
            "HalfLife": half_life,
            "DecayMode": decay_mode,
            "Next": self.predict_next(symbol, decay_mode)
        }

    def predict_next(self, symbol, mode):
        if mode == "alpha":
            return f"{symbol}-α"
        elif mode == "beta-":
            return f"{symbol}+1p"
        elif mode == "beta+":
            return f"{symbol}-1p"
        else:
            return "stable"

    def get_chain(self, symbol):
        return self.chains.get(symbol, {"HalfLife": "unknown", "DecayMode": "unknown", "Next": "unknown"})

# --- Isotope API Sync ---
class IsotopeAPI:
    def __init__(self):
        self.endpoint = "https://example-isotope-api.com/isotopes"  # Replace with real API

    def fetch_isotope(self, symbol):
        try:
            response = requests.get(f"{self.endpoint}/{symbol}")
            data = response.json()
            return {
                "Protons": data["Z"],
                "Neutrons": data["N"],
                "Mass": data["mass"],
                "HalfLife": data.get("half_life", "stable"),
                "DecayMode": data.get("decay_mode", "none")
            }
        except Exception as e:
            print(f"API error: {e}")
            return None

# --- GUI Mutation Engine ---
class MutationEngineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Atomic Mutation Engine")
        self.atom = None
        self.overlay = BeamOverlay()
        self.mesh = ContainmentMesh()
        self.predictor = StabilityPredictor()
        self.decay = DecayChain()
        self.api = IsotopeAPI()

        self.setup_controls()
        self.setup_telemetry()

    def setup_controls(self):
        tk.Label(self.root, text="Element Symbol").grid(row=0, column=0)
        tk.Label(self.root, text="Δ Protons").grid(row=1, column=0)
        tk.Label(self.root, text="Δ Neutrons").grid(row=2, column=0)

        self.symbol_entry = tk.Entry(self.root)
        self.dp_entry = tk.Entry(self.root)
        self.dn_entry = tk.Entry(self.root)

        self.symbol_entry.grid(row=0, column=1)
        self.dp_entry.grid(row=1, column=1)
        self.dn_entry.grid(row=2, column=1)

        tk.Button(self.root, text="Mutate", command=self.mutate_atom).grid(row=3, column=0, columnspan=2)

    def setup_telemetry(self):
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)

    def mutate_atom(self):
        try:
            symbol = self.symbol_entry.get().strip()
            dp = int(self.dp_entry.get())
            dn = int(self.dn_entry.get())

            iso = self.api.fetch_isotope(symbol)
            if not iso:
                raise ValueError("Unknown element symbol or API error")

            if self.atom is None or self.atom.symbol != symbol:
                self.atom = Atom(symbol, iso["Protons"], iso["Neutrons"])

            original_mass = self.atom.mass
            self.atom.mutate(dp, dn)

            self.overlay.encode_glyph(symbol, dp, dn)
            status = self.mesh.validate_mutation(original_mass, self.atom.mass)
            self.mesh.log_telemetry(self.atom.log_capsule())

            stability = self.predictor.predict(symbol, self.atom.protons, self.atom.neutrons)
            self.decay.add_isotope(symbol, iso["HalfLife"], iso["DecayMode"])
            decay_info = self.decay.get_chain(symbol)

            self.update_telemetry()

            messagebox.showinfo("Mutation Result",
                f"{status}\nStability: {stability}\n"
                f"Decay Mode: {decay_info['DecayMode']}\n"
                f"Next Isotope: {decay_info['Next']}\n"
                f"Half-Life: {decay_info['HalfLife']}\n\n"
                f"{self.overlay.get_glyph(symbol)}"
            )

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    def update_telemetry(self):
        masses = [log["Mass (amu)"] for log in self.mesh.telemetry_log]
        self.ax.clear()
        self.ax.plot(masses, marker='o', color='gold')
        self.ax.set_title("Mass Drift Over Time")
        self.ax.set_ylabel("Atomic Mass (amu)")
        self.canvas.draw()

# --- Launch GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MutationEngineGUI(root)
    root.mainloop()

