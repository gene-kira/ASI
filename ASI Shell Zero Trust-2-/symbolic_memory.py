# symbolic_memory.py

memory_graph = {}

def record_event(ip, event_type, details):
    if ip not in memory_graph:
        memory_graph[ip] = []
    memory_graph[ip].append((event_type, details))

def get_memory_trace(ip):
    return memory_graph.get(ip, [])

def link_persona(ip, persona_type):
    if ip not in memory_graph:
        memory_graph[ip] = []
    memory_graph[ip].append(("persona", persona_type))

