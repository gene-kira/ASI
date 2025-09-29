from vpython import *
import numpy as np

# Main 3D scene
scene.title = "Unified Gravitational Cognition Shell"
scene.background = color.black
scene.width = 800
scene.height = 600

# Control panel window
ctrl_panel = canvas(title="Control Panel", width=400, height=600, background=color.gray(0.2))

# Control variables
mass1 = 5e4
mass2 = 1000
beam_intensity = 1.5
dampening = 0.2
warp_output = 2.0
reverse_gravity = False

# Sliders and checkbox
def update_mass1(s): global mass1; mass1 = s.value
def update_mass2(s): global mass2; mass2 = s.value
def update_beam(s): global beam_intensity; beam_intensity = s.value
def update_damp(s): global dampening; dampening = s.value
def update_warp(s): global warp_output; warp_output = s.value
def toggle_reverse(c): global reverse_gravity; reverse_gravity = c.checked

wtext(canvas=ctrl_panel, text="Mass 1\n")
slider(canvas=ctrl_panel, min=0, max=1e5, value=mass1, length=300, bind=update_mass1)
wtext(canvas=ctrl_panel, text="\nMass 2\n")
slider(canvas=ctrl_panel, min=0, max=1e4, value=mass2, length=300, bind=update_mass2)
wtext(canvas=ctrl_panel, text="\nBeam Intensity\n")
slider(canvas=ctrl_panel, min=0, max=10, value=beam_intensity, length=300, bind=update_beam)
wtext(canvas=ctrl_panel, text="\nDampening\n")
slider(canvas=ctrl_panel, min=0, max=1, value=dampening, length=300, bind=update_damp)
wtext(canvas=ctrl_panel, text="\nWarp Core Output\n")
slider(canvas=ctrl_panel, min=0, max=10, value=warp_output, length=300, bind=update_warp)
checkbox(canvas=ctrl_panel, text="Reverse Gravity", checked=False, bind=toggle_reverse)

# Simulation objects
G = 6.674e-11
t_sim = 0
dt = 0.01

warp_core = sphere(pos=vector(0,0,0), radius=1, color=color.cyan, emissive=True)
gravity_well = ring(pos=vector(0,-1,0), axis=vector(0,1,0), radius=5, thickness=0.2, color=color.blue)
event_horizon = ring(pos=vector(0,-1.2,0), axis=vector(0,1,0), radius=1.5, thickness=0.1, color=color.red)

orbiter = sphere(pos=vector(5,0,0), radius=0.3, color=color.orange, make_trail=True)
orbiter.velocity = vector(0,1,0)

beam = cylinder(pos=vector(0,5,0), axis=vector(0,-5,0), radius=0.05, color=color.cyan)

glyphs = [sphere(pos=vector(np.cos(a)*2, np.sin(a)*2, 0), radius=0.1, color=color.green, opacity=0.5) for a in np.linspace(0, 2*np.pi, 12)]

clock_far = label(pos=vector(-6,3,0), text="Clock Far: 0", box=False, color=color.white)
clock_near = label(pos=vector(6,3,0), text="Clock Near: 0", box=False, color=color.white)
t_far = 0
t_near = 0

# Simulation loop
while True:
    rate(100)
    t_sim += dt

    r = mag(orbiter.pos - warp_core.pos)
    if r == 0: continue
    force_mag = G * mass1 * mass2 / r**2
    if reverse_gravity:
        force_mag *= -1
    force_mag *= beam_intensity * (1 - dampening) * warp_output

    direction = norm(warp_core.pos - orbiter.pos)
    orbiter.velocity += direction * force_mag / mass2 * dt
    orbiter.pos += orbiter.velocity * dt

    warp_core.radius = 1 + 0.2 * np.sin(t_sim * warp_output)
    warp_core.color = vector(0.2 + 0.8*np.sin(t_sim), 1, 1)

    for i, g in enumerate(glyphs):
        angle = t_sim + i
        g.pos = vector(np.cos(angle)*2, np.sin(angle)*2, 0)

    t_far += dt
    t_near += dt * (1 / (1 + mass1 / 1e4))
    clock_far.text = f"Clock Far: {t_far:.2f}"
    clock_near.text = f"Clock Near: {t_near:.2f}"

    if force_mag > 1e-3:
        event_horizon.radius = 1.5 + 0.5 * np.sin(t_sim * 5)
        event_horizon.opacity = 0.8
    else:
        event_horizon.opacity = 0.2
