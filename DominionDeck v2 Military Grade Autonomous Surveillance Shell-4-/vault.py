import json
from config import VAULT_PATH

def load_vault():
    try:
        with open(VAULT_PATH, "r") as f:
            return json.load(f)
    except:
        return {"allow": [], "block": []}

def update_vault(ip, action):
    vault = load_vault()
    if action == "allow" and ip not in vault["allow"]:
        vault["allow"].append(ip)
    elif action == "block" and ip not in vault["block"]:
        vault["block"].append(ip)
    with open(VAULT_PATH, "w") as f:
        json.dump(vault, f)

