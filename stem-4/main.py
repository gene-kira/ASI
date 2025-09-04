import threading
from genre_overlay import launch_magicbox_gui
from network_overlay import launch_network_gui
from defense_asi import start_defense_monitor
from mutation_engine import start_mutation_monitor

# Feedback triggers
def mutation_trigger():
    print("[🜂] Mutation event triggered.")

def defense_trigger():
    print("[🛡️] Defense ASI event triggered.")

def launch_daemon():
    # Launch background modules
    threading.Thread(target=launch_network_gui, daemon=True).start()
    threading.Thread(target=start_mutation_monitor, args=(mutation_trigger,), daemon=True).start()
    threading.Thread(target=start_defense_monitor, args=(defense_trigger,), daemon=True).start()

    # Launch GUI
    launch_magicbox_gui(on_mutation=mutation_trigger, on_defense=defense_trigger)

if __name__ == "__main__":
    launch_daemon()

