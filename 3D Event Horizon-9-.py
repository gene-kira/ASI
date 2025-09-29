# tensor_gravity_shell.py

# 🔄 Autoloader
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.animation as animation

# 🌌 Tensor Gravity Shell
class TensorGravityShell:
    def __init__(self, bodies, dt=0.01):
        self.bodies = bodies  # [{'mass': m, 'position': [x,y], 'velocity': [vx,vy]}]
        self.G = 6.67430e-11
        self.c = 299792458
        self.dt = dt
        self.glyph_log = []

    def compute_tensor_force(self, body_i, body_j):
        r_vec = np.array(body_j['position']) - np.array(body_i['position'])
        r = np.linalg.norm(r_vec)
        if r == 0: return np.zeros(2)
        v_rel = np.linalg.norm(np.array(body_j['velocity']) - np.array(body_i['velocity']))
        base_force = self.G * body_i['mass'] * body_j['mass'] / r**2
        correction = 1 + (v_rel**2 / self.c**2)
        force_vec = base_force * correction * (r_vec / r)
        self.glyph_log.append(f"⧉ Tensor mutation: Δv={v_rel:.2f} → correction={correction:.6f}")
        return force_vec

    def relativistic_effects(self, body):
        v = np.linalg.norm(body['velocity'])
        gamma = 1 / np.sqrt(1 - (v**2 / self.c**2)) if v < self.c else np.inf
        body['rel_mass'] = body['mass'] * gamma
        body['time_dilation'] = np.sqrt(1 - (v**2 / self.c**2)) if v < self.c else 0
        self.glyph_log.append(f"⏳ Time dilation: γ={gamma:.6f}, Δt'={body['time_dilation']:.6f}")
        self.glyph_log.append(f"⨀ Relativistic mass: m'={body['rel_mass']:.2e}")

    def update_positions(self):
        forces = [np.zeros(2) for _ in self.bodies]
        for i, bi in enumerate(self.bodies):
            for j, bj in enumerate(self.bodies):
                if i != j:
                    forces[i] += self.compute_tensor_force(bi, bj)
        for i, body in enumerate(self.bodies):
            self.relativistic_effects(body)
            acc = forces[i] / body['rel_mass']
            body['velocity'] += acc * self.dt
            body['position'] += body['velocity'] * self.dt

    def narrate_glyphs(self):
        print("\n🔮 Mutation Glyphs:")
        for glyph in self.glyph_log:
            print(glyph)
        self.glyph_log.clear()

# 🖼️ GUI Feedback + Lensing Overlay
def simulate(shell, steps=500):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(-2e11, 2e11)
    ax.set_ylim(-2e11, 2e11)
    patches = [Circle(body['position'], 1e10, color='blue') for body in shell.bodies]
    for patch in patches:
        ax.add_patch(patch)

    def update(frame):
        shell.update_positions()
        for patch, body in zip(patches, shell.bodies):
            patch.center = body['position']
            # ⦿ Lensing overlay
            if body['rel_mass'] > 1e30:
                patch.set_color('gold')
                shell.glyph_log.append(f"⦿ Lensing zone near mass={body['rel_mass']:.2e}")
        shell.narrate_glyphs()
        return patches

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=50, blit=True)
    plt.show()

# 🚀 Launch Ritual
if __name__ == "__main__":
    # Example: Sun and Earth
    sun = {
        'mass': 1.989e30,
        'position': np.array([0.0, 0.0]),
        'velocity': np.array([0.0, 0.0])
    }
    earth = {
        'mass': 5.972e24,
        'position': np.array([1.496e11, 0.0]),
        'velocity': np.array([0.0, 29780.0])
    }
    shell = TensorGravityShell([sun, earth], dt=60*60)
    simulate(shell, steps=1000)
