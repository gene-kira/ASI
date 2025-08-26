# saver.py
import os
import json

def save_memory(memory, fusion, path):
    try:
        file_path = os.path.join(path, "magicbox_knowledge.json")
        with open(file_path, "w") as f:
            json.dump(memory + fusion, f, indent=2)
        return True
    except Exception as e:
        print(f"Save memory failed: {e}")
        return False

def save_mutation(code, mutation_id, path):
    try:
        filename = f"mutation_{mutation_id}.py"
        file_path = os.path.join(path, filename)
        with open(file_path, "w") as f:
            f.write(code)
        return True
    except Exception as e:
        print(f"Save mutation failed: {e}")
        return False

