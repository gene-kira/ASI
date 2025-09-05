import psutil
from datetime import datetime

def detect_density_spike(flows):
    """
    Detects entropy spikes across recent data flows.
    Returns True if variance and average entropy exceed thresholds.
    """
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    entropies = [f["entropy"] for f in recent]
    avg = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 100 and avg > 500

def initiate_mutation_vote():
    """
    Initiates a mutation vote based on CPU core load.
    Returns True if majority of first 5 cores exceed 50% usage.
    """
    loads = psutil.cpu_percent(percpu=True)
    votes = [load > 50 for load in loads[:5]]
    return votes.count(True) >= 3

def rewrite_optimization_logic():
    """
    Rewrites system optimization logic based on current memory usage.
    Returns a mutation entry for codex logging.
    """
    threshold = psutil.virtual_memory().percent
    logic = f"memory_usage_percent > {threshold}"
    print(f"[🧠 Rewrite] New logic: {logic}")
    return {
        "logic": logic,
        "timestamp": datetime.now().isoformat(),
        "trigger": "recursive_density_spike",
        "consensus": "mutation_vote_passed"
    }

