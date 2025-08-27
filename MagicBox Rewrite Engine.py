# ✅ Auto-loader for required libraries
try:
    import json, os, time
    from random import randint, choice
    import tkinter as tk
    from tkinter import messagebox
except ImportError as e:
    print(f"[❌ Missing Library] {e.name}. Please install it before running.")
    exit(1)

CODEX_FILE = "fusion_codex.json"

# 🧠 Detect symbolic density spike
def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    entropies = [p.entropy for p in flows[-10:]]
    avg = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    if variance > 2.5 and avg > 7.0:
        log_density_spike(entropies, avg)
        return True
    return False

def log_density_spike(entropies, avg):
    print(f"[⚡ Spike] Avg Entropy: {avg:.2f}, Values: {entropies}")

# 🗳️ Mutation vote
def initiate_mutation_vote():
    votes = [choice(["yes", "no"]) for _ in range(5)]
    result = votes.count("yes") >= 3
    print(f"[🗳️ Vote] {votes} → {'Passed' if result else 'Rejected'}")
    return result

# 🔁 Rewrite logic
def rewrite_optimization_logic():
    threshold = randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {threshold}")
    return {
        "logic": f"entropy > {threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed",
        "version": get_codex_version()
    }

# 📜 Codex storage
def get_codex_version():
    if not os.path.exists(CODEX_FILE):
        return 1
    with open(CODEX_FILE, "r") as f:
        codex = json.load(f)
    return len(codex) + 1

def store_rewrite_codex(entry):
    if not validate_codex_entry(entry):
        print("[⚠️ Invalid Entry] Skipped")
        return
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)
    print(f"[📦 Codex Updated] Version {entry['version']} stored")

def validate_codex_entry(entry):
    keys = {"logic", "timestamp", "trigger", "consensus", "version"}
    return keys.issubset(entry.keys())

# 🌌 MagicBox GUI Overlay
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🧙 MagicBox Rewrite Engine")
    root.geometry("420x280")
    root.configure(bg="#2b2b3d")

    title = tk.Label(root, text="MagicBox Rewrite Engine", fg="#00ffd0", bg="#2b2b3d", font=("Consolas", 16, "bold"))
    title.pack(pady=10)

    status = tk.Label(root, text="🧘 Awaiting symbolic spike...", fg="white", bg="#2b2b3d", font=("Consolas", 12))
    status.pack(pady=10)

    def trigger_rewrite():
        status.config(text="⚡ Density spike detected")
        root.update()
        time.sleep(0.5)
        if initiate_mutation_vote():
            entry = rewrite_optimization_logic()
            store_rewrite_codex(entry)
            status.config(text=f"✅ Rewrite stored (v{entry['version']})")
        else:
            status.config(text="🛑 Mutation vote rejected")

    trigger_btn = tk.Button(root, text="🧠 One-Click Rewrite", command=trigger_rewrite,
                            bg="#444466", fg="white", font=("Consolas", 12, "bold"), width=25)
    trigger_btn.pack(pady=20)

    root.mainloop()

# 🚀 Launch
if __name__ == "__main__":
    launch_magicbox_gui()

