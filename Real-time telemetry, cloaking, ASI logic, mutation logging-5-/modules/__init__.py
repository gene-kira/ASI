# modules/__init__.py
# Makes 'modules' a valid Python package and re-exports from modules.py

from .modules import (
    get_ip_telemetry,
    get_system_telemetry,
    fuse_telemetry,
    interpret_emotion,
    predictive_cloak,
    fernet,
    store_mutation,
    symbolic_memory,
    mutation_vault,
    MagicBoxGUI
)

