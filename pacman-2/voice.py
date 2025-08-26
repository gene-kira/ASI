# voice.py
import pyttsx3
from config import VOICE_ENABLED, VOICE_RATE, VOICE_VOLUME

engine = pyttsx3.init()
engine.setProperty('rate', VOICE_RATE)
engine.setProperty('volume', VOICE_VOLUME)

def narrate_fusion(fusion_output):
    if not VOICE_ENABLED:
        return
    for item in fusion_output:
        engine.say(f"Fusion complete. {item['source_file']} and port {item['source_port']} created mutation {item['mutation']}.")
    engine.runAndWait()

def narrate_mutation(mutation_id):
    if not VOICE_ENABLED:
        return
    engine.say(f"Mutation {mutation_id} has been saved to the vault.")
    engine.runAndWait()

def narrate_swarm_sync():
    if not VOICE_ENABLED:
        return
    engine.say("Swarm sync complete. Mutations have been replicated.")
    engine.runAndWait()

