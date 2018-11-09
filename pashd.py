#! /usr/bin/env python3

# PASHD - Per-agent Shortest Heurestic Distance
# - Agent uses a heurestic (Manhattan distance) to generate a list of closest safe nodes
# - Using A*, agent finds a path towards the closest one. If that's impossible, it sequentially tries next-best nodes
# - Agent pathfinds to the goal, using LRA* (follows the planned route and in case of imminent collision, it replans)
# - If the goal is already occupied, algorithm begins again, considering agent's current position as the start

from sys import argv
from pqdict import pqdict
from level import NoPathFound, Level
import random

class Agent:
    def __init__(self, agent_id, level):
        self.id = agent_id
        self.level = level
        self.pos = level.scenario.agents[agent_id]
        self.retarget()
    
    def retarget(self, first_move_disallow=set()):
        self.next_path_idx = 1
        self.path = None
        goal_candidates = map(lambda x: (x, self.manhattan_distance(self.pos, x)), self.level.frontier)
        for candidate, _ in sorted(goal_candidates, key=lambda x: x[1]):
            # Currently, agents do not move away from occupied safe nodes so
            # occupied goals can be ignored outright
            if candidate in first_move_disallow: continue
            path = self.pathfind_to(candidate, first_move_disallow)
            if path: 
                self.path = path
                return
    
    def pathfind_to(self, goal, first_move_disallow=set()):
        g = self.level.g
        nan = float("nan")
        closed = set()
        opened = pqdict({self.pos: 0})
        g_costs = {}
        predecessors = {}
        g_costs[self.pos] = 0
        first_move = True
        while len(opened) > 0:
            curr = opened.pop()
            if curr == goal:
                return reconstruct_path(predecessors, goal)
            closed.add(curr)
            for n in g[curr].keys():
                if n in closed: continue
                if first_move and n in first_move_disallow: continue
                considered_g_cost = g_costs[curr] + 1
                if considered_g_cost >= g_costs.get(n, nan):
                    continue
                g_costs[n] = considered_g_cost
                predecessors[n] = curr
                f_cost = considered_g_cost + self.manhattan_distance(n, goal)
                if not n in opened:
                    opened.additem(n, f_cost)
                else:
                    opened[n] = f_cost
            first_move = False
        return None

    def manhattan_distance(self, x, y):
        x_coords = self.level.id_to_coords(x)
        y_coords = self.level.id_to_coords(y)
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
    
    def peek_move(self):
        if self.path == None:
            raise NoPathFound()
        if len(self.path) <= self.next_path_idx:
            return None
        return self.path[self.next_path_idx]
    
    def do_move(self):
        if self.path == None:
            raise NoPathFound()
        if len(self.path) <= self.next_path_idx:
            raise StopIteration()
        self.pos = self.path[self.next_path_idx]
        self.next_path_idx += 1
        return self.pos

def plan_evacuation(level, random_seed=42):
    random.seed(random_seed)
    agents = [Agent(i, level) for i in range(len(level.scenario.agents))]
    agent_paths = [[agent.pos] for agent in agents]
    agent_order = list(range(len(agents)))
    finished = False
    while not finished:
        random.shuffle(agent_order)
        finished = True
        occupied = set()
        # Currently the simplest way to prevent zero-time swaps
        for i in agent_order:
            occupied.add(agents[i].pos)
    
        for i in agent_order:
            next_pos = agents[i].peek_move()
            if next_pos == None: continue
            finished = False
            if next_pos in occupied:
                agents[i].retarget(occupied)
            next_pos = agents[i].do_move()
            agent_paths[i].append(next_pos)
            occupied.add(next_pos)
    return agent_paths
                
def reconstruct_path(predecessors, goal):
    path = [goal]
    while predecessors.get(path[-1], None):
        path.append(predecessors[path[-1]])
    path.reverse()
    return path

def main():
    map_path, scen_path = argv[1], argv[2]
    l = Level(map_path, scen_path)
    paths = plan_evacuation(l)
    for path in paths:
        print(*path)

if __name__ == "__main__":
    main()