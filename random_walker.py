import random

class RandomWalker:
    def __init__(self, network, agents, _):
        self.network = network
        self.agent_positions, self.agent_finishes = list(zip(*agents))
        print(self.agent_positions, self.agent_finishes)
    
    def __iter__(self):
        while True:
            self.agent_positions = [random.choice(list(self.network[pos].keys())) for pos in self.agent_positions]
            yield self.agent_positions