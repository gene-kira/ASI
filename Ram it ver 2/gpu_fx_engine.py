import pygame
import os

def trigger_fx(event_type, value):
    sound_map = {
        "allocate": "allocate.wav",
        "purge": "purge.wav",
        "overload": "boot.wav"
    }
    sound_file = os.path.join("assets", "aura_sounds", sound_map.get(event_type, "boot.wav"))
    pygame.mixer.init()
    pygame.mixer.Sound(sound_file).play()
    print(f"[FX] {event_type.upper()} triggered at {value}")

