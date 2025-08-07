import json
from gui_controller import apply_settings
from swarm_agents import spawn_agents
from purge_daemon import monitor_memory
from gpu_fx_engine import trigger_fx

# Load manifest
with open("manifest.json") as f:
    config = json.load(f)

# Initialize swarm agents
agents = spawn_agents(config["default_size_mb"], config["agent_count"])
print(f"[Swarm] Spawned {len(agents)} agents.")

# Trigger cinematic FX
if config["gpu_fx"]:
    trigger_fx("boot", config["default_size_mb"])

# Start purge daemon if enabled
if config["auto_purge"]:
    monitor_memory()

# Launch GUI
apply_settings()  # This will internally call create_ramdisk and trigger FX

