# mixer.py

def asi_mixer(memory):
    fusion_output = []
    files = [m for m in memory if "file" in m['type']]
    ports = [m for m in memory if "port" in m['type']]

    for f in files:
        for p in ports:
            if abs(f['novelty'] - p['novelty']) < 20:
                mutation_id = hash(f['path'] + str(p['port'])) % 9999
                fusion_output.append({
                    "type": "fusion",
                    "source_file": f['path'],
                    "source_port": p['port'],
                    "mutation": mutation_id,
                    "insight": f"Fusion of {f['path']} + Port {p['port']} yields mutation {mutation_id}",
                    "symbolic_density": (f['weight'] + p['weight']) // 2,
                    "tags": ["fusion", "novelty", "mutation"]
                })

    return fusion_output

