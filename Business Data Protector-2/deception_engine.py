# deception_engine.py

import random
from utils import log_codex

def trigger_deception_overlay(persona):
    """
    Trigger a deception overlay based on the blocked persona.
    """
    log_codex(f"🛡️ Deception overlay triggered for persona: {persona}")
    print(f"🛡️ [DECEPTION] Persona '{persona}' blocked → Overlay activated")
    # You can expand this with GUI overlays, fake alerts, or symbolic feedback

def generate_decoy_ports():
    """
    Simulate decoy port activity to confuse scanners.
    """
    decoys = random.sample(range(1000, 9999), 5)
    log_codex(f"🎭 Decoy ports generated: {decoys}")
    print(f"🎭 [DECOY] Fake ports active: {decoys}")
    # You could visualize these in your threat matrix or swarm panel

def simulate_swarm_echo():
    """
    Emit fake swarm sync pulses to mask real traffic.
    """
    echo_id = random.randint(100000, 999999)
    log_codex(f"🌀 Swarm echo emitted: ID {echo_id}")
    print(f"🌀 [ECHO] Swarm sync pulse: {echo_id}")
    # Could be used to confuse ingest filters or trigger false sync rings

def inject_codex_mutation():
    """
    Mutate symbolic codex logic to simulate adaptive defense.
    """
    mutation = random.choice(["persona shift", "overlay rewrite", "port mask", "memory fork"])
    log_codex(f"🧬 Codex mutation injected: {mutation}")
    print(f"🧬 [MUTATION] Codex logic altered: {mutation}")
    # You could log this to a mutation dashboard or trigger GUI feedback

