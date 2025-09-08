# ip_blocker.py

import subprocess
import threading
from utils import log_codex

def block_ip(ip, direction="in"):
    """
    Block an IP address using Windows Firewall.
    direction: 'in', 'out', or 'both'
    """
    rule_name = f"MythicBlock_{ip}_{direction}"
    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name}",
        f"dir={direction}",
        "action=block",
        f"remoteip={ip}"
    ]
    try:
        subprocess.run(cmd, check=True)
        log_codex(f"🚫 IP blocked: {ip} → Direction: {direction}")
        print(f"🚫 [BLOCKED] {ip} ({direction})")
    except Exception as e:
        log_codex(f"❌ Failed to block IP {ip}: {e}")
        print(f"❌ [ERROR] Block failed for {ip}: {e}")

def unblock_ip(ip, direction="in"):
    """
    Remove a firewall block rule for an IP.
    """
    rule_name = f"MythicBlock_{ip}_{direction}"
    cmd = [
        "netsh", "advfirewall", "firewall", "delete", "rule",
        f"name={rule_name}"
    ]
    try:
        subprocess.run(cmd, check=True)
        log_codex(f"✅ IP unblocked: {ip}")
        print(f"✅ [UNBLOCKED] {ip}")
    except Exception as e:
        log_codex(f"❌ Failed to unblock IP {ip}: {e}")
        print(f"❌ [ERROR] Unblock failed for {ip}: {e}")

def block_ip_temporary(ip, duration=60, direction="in"):
    """
    Block an IP temporarily, then auto-unblock after `duration` seconds.
    """
    block_ip(ip, direction)
    def unblock_later():
        threading.Event().wait(duration)
        unblock_ip(ip, direction)
    threading.Thread(target=unblock_later, daemon=True).start()

