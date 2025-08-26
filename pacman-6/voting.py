# voting.py
def vote_on_mutation(mutation, local_style):
    density = mutation.get("symbolic_density", 50)
    style = mutation.get("style", "unknown")
    score = 0

    if style == local_style:
        score += 30
    if density > 60:
        score += 40
    if "fusion" in mutation.get("tags", []):
        score += 30

    return score >= 70  # Accept if score is high enough

