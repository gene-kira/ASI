from zones import load_ip_map
from gui import launch_gui

if __name__ == "__main__":
    try:
        ip_map = load_ip_map()
        if ip_map:
            launch_gui(ip_map)
        else:
            print("[!] No zones loaded. Aborting.")
    except Exception as e:
        print(f"[!] Fatal error: {e}")

