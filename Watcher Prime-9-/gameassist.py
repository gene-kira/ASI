# gameassist.py — Game Detection + Assist + Visual Intelligence
import uuid, json, os, threading
from datetime import datetime
import psutil
from importlib import import_module
from codex import log_event
from gui import codex_vault, update_codex_display, log_output

# Load external libraries
for lib in ['pygame', 'numpy', 'cv2']:
    try:
        globals()[lib] = import_module(lib)
    except ImportError as e:
        print(f"Missing {lib}: {e}")

GAME_DB_FILE = "game_db.json"

def load_known_games():
    return json.load(open(GAME_DB_FILE)) if os.path.exists(GAME_DB_FILE) else {}

def save_known_game(exe_name, genre):
    games = load_known_games()
    games[exe_name.lower()] = genre
    with open(GAME_DB_FILE, "w") as f:
        json.dump(games, f, indent=2)
    log_output(f"[🎮] Registered: {exe_name} ({genre})")

def detect_active_game():
    known = load_known_games()
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name and name.lower() in known:
            return name.lower(), known[name.lower()]
    return None, None

def activate_game_assist(game_name, genre):
    traits = ["performance_boost", "symbolic_overlay", "swarm_sync"]
    codex_vault.append({
        "id": f"GameAssist_{uuid.uuid4().hex[:6]}",
        "source": f"GameAssist:{game_name}",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": "|".join(traits),
        "status": "active"
    })
    update_codex_display()
    log_output(f"[🎮] Game detected: {game_name} ({genre})")
    log_event(f"GameAssist:{game_name}", "assist", "|".join(traits))
    GameHelper().start_game()

def loop_game_detection():
    game, genre = detect_active_game()
    if game:
        activate_game_assist(game, genre)
    threading.Timer(20, loop_game_detection).start()

# 🧠 Game Intelligence
class GameHelper:
    def __init__(self):
        self.enemy_ai = EnemyAI()
        self.player = Player()
        self.detector = ObjectDetector()

    def start_game(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()
        cap = cv2.VideoCapture(0)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return

            ret, frame = cap.read()
            if not ret: continue

            frame = pygame.surfarray.make_surface(numpy.rot90(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            screen.blit(frame, (0, 0))

            self.enemy_ai.render(screen)
            self.player.update()
            self.detector.detect(screen)

            self.draw_feedback(screen)
            pygame.display.update()
            clock.tick(30)

    def draw_feedback(self, screen):
        try:
            data = getattr(game_state, "performance_data", [])
            if not data: return
            correct = sum(1 for m in data if m['data']['correct'])
            accuracy = correct / len(data)
            color = (0, 255, 0) if accuracy > 0.8 else (255, 255, 0) if accuracy > 0.5 else (255, 0, 0)
            pygame.draw.rect(screen, color, pygame.Rect(10, 60, int(accuracy * 780), 30))
        except Exception as e:
            print(f"[⚠️] Feedback error: {e}")

class EnemyAI:
    def render(self, screen):
        for enemy in getattr(game_state, "enemies", []):
            pygame.draw.circle(screen, (255, 0, 0), (enemy.x, enemy.y), 15)
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(enemy.x - 10, enemy.y - 20, 20 * (enemy.health / enemy.max_health), 5))

class Player:
    def __init__(self):
        self.health = 100
        self.max_health = 300

    def update(self):
        if self.health < self.max_health:
            self.health += min(10, self.max_health - self.health)

class ObjectDetector:
    def detect(self, screen):
        try:
            frame = pygame.surfarray.array3d(screen)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
                if cv2.contourArea(c) > 100:
                    x, y, w, h = cv2.boundingRect(c)
                    pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(x, y, w, h), 2)
                    pygame.draw.circle(screen, (255, 255, 0), (x + w // 2, y + h // 2), 5)
        except Exception as e:
            print(f"[⚠️] Object detection error: {e}")

