# mutation.py

from random import choice
import time

class MutationEvent:
    def __init__(self, node_id, entropy, timestamp, votes):
        self.node_id = node_id              # Node that triggered the mutation
        self.entropy = entropy              # Entropy level at trigger
        self.timestamp = timestamp          # Time of mutation
        self.votes = votes                  # List of "yes"/"no" votes
        self.passed = votes.count("yes") >= 3  # Mutation passes if 3+ yes votes

def initiate_mutation_vote():
    # Simulate swarm voting with 5 randomized votes
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes, votes.count("yes") >= 3

