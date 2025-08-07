# queen_defender.py
import subprocess

class Defender:
    def __init__(self):
        self.audit_log = []

    def run_powershell(self, command):
        full_cmd = ["powershell", "-Command", command]
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def scan_quick(self):
        output = self.run_powershell("Start-MpScan -ScanType QuickScan")
        self.audit_log.append("glyph(scan:quick)")
        return output

    def scan_full(self):
        output = self.run_powershell("Start-MpScan -ScanType FullScan")
        self.audit_log.append("glyph(scan:full)")
        return output

    def get_threats(self):
        output = self.run_powershell("Get-MpThreat")
        self.audit_log.append("glyph(threats:query)")
        return output

    def add_firewall_rule(self, name, program_path):
        cmd = f'New-NetFirewallRule -DisplayName "{name}" -Direction Inbound -Program "{program_path}" -Action Allow'
        output = self.run_powershell(cmd)
        self.audit_log.append(f"glyph(firewall:add:{name})")
        return output

    def remove_firewall_rule(self, name):
        cmd = f'Remove-NetFirewallRule -DisplayName "{name}"'
        output = self.run_powershell(cmd)
        self.audit_log.append(f"glyph(firewall:remove:{name})")
        return output

    def get_audit_log(self):
        return self.audit_log[-5:]

