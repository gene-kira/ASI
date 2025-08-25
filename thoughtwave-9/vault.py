from cryptography.fernet import Fernet

# 🔐 Generate encryption key and vault instance
vault_key = Fernet.generate_key()
vault = Fernet(vault_key)

def log_mutation(result):
    entry = f"{result['fusion_signature']}|{result['weight']}|{','.join(result['tags'])}"
    encrypted = vault.encrypt(entry.encode())

    with open("mutation_vault.log", "ab") as f:
        f.write(encrypted + b"\n")

