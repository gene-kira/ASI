# --- Part 1: File Watcher + Data Parser ---
import os
import sys
import time
import threading
import json
import csv
import xml.etree.ElementTree as ET
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INGEST_FOLDER = "./ingest"

# --- Real Data Parser ---
def parse_file(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".json":
            with open(file_path, "r") as f:
                data = json.load(f)
                return str(data)
        elif ext == ".txt":
            with open(file_path, "r") as f:
                return f.read()
        elif ext == ".csv":
            with open(file_path, newline='') as f:
                reader = csv.reader(f)
                rows = [", ".join(row) for row in reader]
                return "\n".join(rows)
        elif ext == ".xml":
            tree = ET.parse(file_path)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        else:
            return "Unsupported file type"
    except Exception as e:
        return f"Error parsing file: {e}"

# --- File Watcher ---
class IngestWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[Auto-Ingest] {event.src_path}")
            threading.Thread(target=start_vortex, args=(event.src_path,), daemon=True).start()

def start_watcher():
    os.makedirs(INGEST_FOLDER, exist_ok=True)
    observer = Observer()
    observer.schedule(IngestWatcher(), INGEST_FOLDER, recursive=False)
    observer.start()
    print(f"[Watcher] Monitoring {INGEST_FOLDER} for new files...")
    return observer

# --- Part 2: Vortex Visualization + HUD Overlay ---
import pygame
import math
import random

def start_vortex(file_path):
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mythic Vortex Event Horizon")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Consolas", 16)

        particles = []
        center = (400, 300)
        angle = 0

        raw_data = parse_file(file_path)
        seed = sum([ord(c) for c in raw_data]) % 360
        color_shift = [(seed * 3) % 255, (seed * 7) % 255, (seed * 11) % 255]

        running = True
        start_time = time.time()
        while running:
            screen.fill((0, 0, 20))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if time.time() - start_time > 15:
                running = False

            for _ in range(5):
                radius = random.randint(50, 250)
                theta = math.radians(angle + random.randint(-30, 30))
                x = center[0] + radius * math.cos(theta)
                y = center[1] + radius * math.sin(theta)
                particles.append({
                    'pos': [x, y],
                    'vel': [0, 0],
                    'color': (
                        (color_shift[0] + random.randint(-20, 20)) % 255,
                        (color_shift[1] + random.randint(-20, 20)) % 255,
                        (color_shift[2] + random.randint(-20, 20)) % 255
                    )
                })

            for p in particles:
                dx = center[0] - p['pos'][0]
                dy = center[1] - p['pos'][1]
                dist = math.hypot(dx, dy)
                if dist > 5:
                    p['vel'][0] += dx / dist * 0.5
                    p['vel'][1] += dy / dist * 0.5
                p['pos'][0] += p['vel'][0]
                p['pos'][1] += p['vel'][1]
                pygame.draw.circle(screen, p['color'], (int(p['pos'][0]), int(p['pos'][1])), 3)

            # HUD Overlay
            hud_text = font.render(f"Data Seed: {seed}", True, (200, 200, 255))
            screen.blit(hud_text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
    except Exception as e:
        print(f"[Error] Vortex failed to load: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    observer = start_watcher()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Shutdown] Stopping watcher...")
        observer.stop()
    observer.join()

