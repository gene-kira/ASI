from cryptography.fernet import Fernet
import random
from modules.vault import symbolic_memory

fernet = Fernet(Fernet.generate_key())

def symbolic_overlay(entropy):
    if entropy > 80: return "🧿"
    elif entropy > 50: return "🔺"
    else: return "🌀"

def predictive_cloak(data, entropy, emotion):
    if entropy > 70 or emotion in ["⚠️ ALERT", "🔶 TENSION"]:
        encoded = fernet.encrypt(str(data).encode())
        overlay = symbolic_overlay(entropy)
        mutation_id = f"MUT-{random.randint(1000,9999)}-{overlay}"
        symbolic_memory["mutations"].append(mutation_id)
        return encoded, mutation_id
    return None, None

