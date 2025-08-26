# voice.py
import pyttsx3
import config

engine = pyttsx3.init()
engine.setProperty('rate', config.VOICE_RATE)
engine.setProperty('volume', config.VOICE_VOLUME)

def narrate_fusion(fusion_output):
    if not config.VOICE_ENABLED:
        return
    for item in fusion_output:
        engine.say(f"Fusion complete. {item['source_file']} and port {item['source_port']} created mutation {item['mutation']}.")
    engine.runAndWait()

def narrate_mutation(mutation_id):
    if not config.VOICE_ENABLED:
        return
    engine.say(f"Mutation {mutation_id} has been saved to the vault.")
    engine.runAndWait()

def narrate_swarm_sync():
    if not config.VOICE_ENABLED:
        return
    engine.say("Swarm sync complete. Mutations have been replicated.")
    engine.runAndWait()

