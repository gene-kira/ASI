# modules/modules.py
# Central manifest for VeilMind Nexus modules

from .telemetry import get_ip_telemetry
from .system_pulse import get_system_telemetry
from .fusion_logic import fuse_telemetry, interpret_emotion
from .cloaking import predictive_cloak, fernet
from .vault import store_mutation, symbolic_memory, mutation_vault
from .gui import MagicBoxGUI

__all__ = [
    "get_ip_telemetry",
    "get_system_telemetry",
    "fuse_telemetry",
    "interpret_emotion",
    "predictive_cloak",
    "fernet",
    "store_mutation",
    "symbolic_memory",
    "mutation_vault",
    "MagicBoxGUI"
]

