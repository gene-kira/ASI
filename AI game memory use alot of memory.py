# Script 1: Core Loader + Input + Screen Watcher
import os, sys, subprocess, threading, time
import tkinter as tk
from tkinter import ttk

required_libs = ['pynput', 'Pillow', 'opencv-python', 'pyttsx3', 'numpy', 'psutil']
def install_libs():
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
install_libs()

from pynput import keyboard, mouse
from PIL import ImageGrab
import cv2
import numpy as np
import pyttsx3
import psutil

class KeyLogger:
    def __init__(self):
        self.key_log = []
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._log_keys, daemon=True).start()

    def stop(self):
        self.running = False

    def _log_keys(self):
        def on_press(key):
            if self.running:
                self.key_log.append((time.time(), str(key)))
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

class MouseLogger:
    def __init__(self):
        self.mouse_log = []
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._log_mouse, daemon=True).start()

    def stop(self):
        self.running = False

    def _log_mouse(self):
        def on_click(x, y, button, pressed):
            if self.running:
                self.mouse_log.append((time.time(), x, y, str(button), pressed))
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

class ScreenWatcher:
    def __init__(self):
        self.frames = []
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _capture_loop(self):
        while self.running:
            img = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self.frames.append((time.time(), frame))
            time.sleep(1)

# Script 2: Game Detection + Strategy Engine
class GameWatcher:
    def __init__(self, target_exes):
        self.target_exes = target_exes
        self.running = False
        self.callback = None

    def start(self, on_game_detected):
        self.callback = on_game_detected
        self.running = True
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _watch_loop(self):
        while self.running:
            active = [p.name().lower() for p in psutil.process_iter()]
            for exe in self.target_exes:
                if exe.lower() in active:
                    print(f"[GameWatcher] Detected game: {exe}")
                    self.callback()
                    self.running = False
                    return
            time.sleep(2)

class StrategyLearner:
    def __init__(self):
        self.tactic_tree = {}

    def analyze_session(self, key_log, mouse_log, frames):
        for ts, frame in frames:
            red_alert = np.sum(frame[:, :, 2] > 200)
            if red_alert > 10000:
                self.tactic_tree[ts] = "Enemy spotted"

# Script 3: Swarm + Voice-Only HUD + Daemon
class SwarmTactics:
    def __init__(self):
        self.swarm_memory = []

    def add_strategy(self, tactic_tree):
        self.swarm_memory.append(tactic_tree)
        self.evolve()

    def evolve(self):
        evolved = []
        for tree in self.swarm_memory:
            mutated = {k: v + " (mutated)" for k, v in tree.items()}
            evolved.append(mutated)
        self.swarm_memory = evolved

class VoiceCaster:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

class StrategyDaemon:
    def __init__(self):
        self.rewrite_log = []

    def evaluate(self, tactic_tree, key_log):
        panic_score = sum(1 for ts, action in key_log if "Key" in action)
        if panic_score > 50:
            self.rewrite(tactic_tree, reason="High panic score")

    def rewrite(self, tactic_tree, reason):
        mutated = {k: v + " → switch to stealth" for k, v in tactic_tree.items()}
        self.rewrite_log.append((time.time(), reason, mutated))
        print(f"[Daemon] Rewriting strategy due to: {reason}")

    def save_log(self):
        os.makedirs("magicbox_logs", exist_ok=True)
        with open("magicbox_logs/mutation_log.txt", "w") as f:
            for ts, reason, tree in self.rewrite_log:
                f.write(f"{time.ctime(ts)} | {reason}\n")
                for k, v in tree.items():
                    f.write(f"  {k}: {v}\n")
                f.write("\n")

# Script 4: GUI + Voice-Only HUD Integration
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙 Mythic Strategist v2.1")
        self.root.geometry("400x450")
        self.root.configure(bg="#1e1e2f")

        self.keylogger = KeyLogger()
        self.mouselogger = MouseLogger()
        self.watcher = ScreenWatcher()
        self.learner = StrategyLearner()
        self.swarm = SwarmTactics()
        self.voice = VoiceCaster()
        self.daemon = StrategyDaemon()
        self.game_watcher = GameWatcher(["eldenring.exe", "skyrim.exe", "doom.exe"])

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#3e3e5f", foreground="white")
        style.map("TButton", background=[("active", "#5e5e8f")])

        self.status = tk.StringVar(value="Status: Idle")

        ttk.Label(root, text="🧠 Mythic Strategist v2.1", font=("Segoe UI", 16), background="#1e1e2f", foreground="#cfcfff").pack(pady=20)
        ttk.Button(root, text="Start Watching", command=self.start_all).pack(pady=10)
        ttk.Button(root, text="Stop & Analyze", command=self.stop_all).pack(pady=10)
        ttk.Label(root, textvariable=self.status, font=("Segoe UI", 12), background="#1e1e2f", foreground="#aaffaa").pack(pady=20)

    def start_all(self):
        self.status.set("Status: Watching...")
        self.keylogger.start()
        self.mouselogger.start()
        self.watcher.start()
        self.game_watcher.start(self.on_game_detected)

    def stop_all(self):
        self.status.set("Status: Analyzing...")
        self.keylogger.stop()
        self.mouselogger.stop()
        self.watcher.stop()
        self.learner.analyze_session(self.keylogger.key_log, self.mouselogger.mouse_log, self.watcher.frames)
        self.swarm.add_strategy(self.learner.tactic_tree)
        self.voice.speak("Strategy analysis complete.")
        self.daemon.evaluate(self.learner.tactic_tree, self.keylogger.key_log)
        self.daemon.save_log()
        self.status.set("Status: Complete")

    def on_game_detected(self):
        self.voice.speak("Game detected. Strategy mode activated.")
        self.status.set("Status: Game Detected")

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

