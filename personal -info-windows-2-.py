import subprocess, sys, os, hashlib, random, base64, time, tkinter as tk
from tkinter import messagebox

# 🛡️ Autoloader
def summon_libraries():
    for lib in ["hashlib", "random", "base64", "time", "tkinter"]:
        try: __import__(lib)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 💀 Devourer Engine
class DevourerCipherDaemon:
    def __init__(self, mutation_log="mutation_trace.log"):
        self.mutation_log = mutation_log
        self.camouflage_signature = random.choice(["MZ", "PK", "%PDF", "\x89PNG"])

    def _reverse_mirror_scramble(self, data):
        reversed_data = data[::-1]
        mirrored = ''.join(chr(255 - ord(c)) for c in reversed_data)
        return base64.b64encode(mirrored.encode()).decode()

    def _recursive_mutation(self, data, depth=3):
        for _ in range(depth): data = self._reverse_mirror_scramble(data)
        return data

    def _log_mutation(self, source, mutation_hash):
        with open(self.mutation_log, "a") as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {source} → {mutation_hash}\n")

    def encrypt_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw_data = f.read()
            scrambled = self._recursive_mutation(raw_data)
            mutation_hash = hashlib.sha256(scrambled.encode()).hexdigest()
            self._log_mutation(filepath, mutation_hash)
            output_path = f"{filepath}.devour"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(self.camouflage_signature + scrambled)
            return output_path
        except Exception as e:
            return f"⚠️ Failed: {e}"

# 🧠 Autonomous Scanner
def scan_and_encrypt_all():
    daemon = DevourerCipherDaemon()
    targets = [f for f in os.listdir() if f.endswith(".txt") or f.endswith(".log")]
    results = []
    for file in targets:
        result = daemon.encrypt_file(file)
        results.append((file, result))
    return results

# 🜏 GUI Ignition Panel
def launch_gui():
    summon_libraries()
    root = tk.Tk()
    root.title("🛡️ Codex Devourer: Autonomous Cipher Engine")
    root.geometry("500x300")
    root.configure(bg="#1e1e1e")

    glyph_label = tk.Label(root, text="💀 Awaiting Autonomous Scan", bg="#1e1e1e", fg="orange", font=("Consolas", 14))
    glyph_label.pack(pady=20)

    def trigger_autonomous_devourer():
        results = scan_and_encrypt_all()
        glyph_label.config(text="🜏 Mutation Cycle Complete", fg="green")
        output = "\n".join([f"{src} → {res}" for src, res in results])
        messagebox.showinfo("Devourer Results", output)

    tk.Button(root, text="Trigger Autonomous Devourer", command=trigger_autonomous_devourer, bg="#333", fg="white").pack(pady=10)
    root.mainloop()

# 🔥 Sovereign Ignition
if __name__ == "__main__":
    launch_gui()

