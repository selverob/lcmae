#! /usr/bin/env python3

# PASHD - Per-agent Shortest Heurestic Distance
# - Agent uses a heurestic (Manhattan distance) to generate
#   a list of closest safe nodes
# - Using A*, agent finds a path towards the closest one.
#   If that's impossible, it sequentially tries next-best nodes
# - Agent pathfinds to the goal, using LRA*
#   (follows the planned route and in case of imminent collision, it replans)
# - If the goal is already occupied, algorithm begins again,
#   considering agent's current position as the start

import random
from pqdict import pqdict
from sys import argv, stderr
from typing import Dict, List, Optional
from level import Level


class Agent:
    def __init__(self, agent_id: int, level: Level):
        self.id = agent_id
        self.level = level
        self.taken_path = [level.scenario.agents[agent_id]]
        self.retarget()

    @property
    def pos(self) -> int:
        return self.taken_path[-1]

    def retarget(self, first_move_disallow=set()):
        self.next_path_idx = 1
        self.future_path = None
        goal_candidates = map(
            lambda x: (x, self.manhattan_distance(self.pos, x)),
            self.level.frontier)
        for candidate, _ in sorted(goal_candidates, key=lambda x: x[1]):
            # Currently, agents do not move away from occupied safe nodes so
            # occupied goals can be ignored outright
            if candidate in first_move_disallow:
                continue
            path = self.pathfind_to(candidate, first_move_disallow)
            if path:
                self.future_path = path
                return

    def pathfind_to(self,
                    goal: int,
                    first_move_disallow=set()) -> Optional[List[int]]:
        g = self.level.g
        nan = float("nan")
        closed = set()
        opened = pqdict({self.pos: 0})
        g_costs: Dict[int, float] = {}
        predecessors: Dict[int, int] = {}
        g_costs[self.pos] = 0
        first_move = True
        while len(opened) > 0:
            curr = opened.pop()
            if curr == goal:
                return reconstruct_path(predecessors, goal)
            closed.add(curr)
            for n in g[curr].keys():
                if n in closed:
                    continue
                if first_move and n in first_move_disallow:
                    continue
                considered_g_cost = g_costs[curr] + 1
                if considered_g_cost >= g_costs.get(n, nan):
                    continue
                g_costs[n] = considered_g_cost
                predecessors[n] = curr
                f_cost = considered_g_cost + self.manhattan_distance(n, goal)
                if n not in opened:
                    opened.additem(n, f_cost)
                else:
                    opened[n] = f_cost
            first_move = False
        return None

    def manhattan_distance(self, x: int, y: int) -> int:
        x_coords = self.level.id_to_coords(x)
        y_coords = self.level.id_to_coords(y)
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])

    def peek_move(self):
        if self.future_path is None:
            return self.pos
        if len(self.future_path) <= self.next_path_idx:
            return None
        return self.future_path[self.next_path_idx]

    def do_move(self):
        if self.future_path is None:
            print("Agent {} has no path, staying at {}"
                  .format(self.id, self.pos),
                  file=stderr)
            self.taken_path.append(self.pos)
            return self.pos
        if len(self.future_path) <= self.next_path_idx:
            raise StopIteration()
        self.taken_path.append(self.future_path[self.next_path_idx])
        self.next_path_idx += 1
        return self.pos


def plan_evacuation(level, random_seed=42):
    random.seed(random_seed)
    agents = [Agent(i, level) for i in range(len(level.scenario.agents))]
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
            if next_pos is None:
                continue
            if next_pos in occupied:
                agents[i].retarget(occupied)
            current_pos = agents[i].pos
            next_pos = agents[i].do_move()
            if current_pos != next_pos:
                finished = False
            occupied.add(next_pos)
    return [agent.taken_path for agent in agents]


def reconstruct_path(predecessors, goal):
    path = [goal]
    while predecessors.get(path[-1], None):
        path.append(predecessors[path[-1]])
    path.reverse()
    return path


def main():
    map_path, scen_path = argv[1], argv[2]
    lvl = Level(map_path, scen_path)
    if len(lvl.frontier) == 0:
        print("No passage to safety exists!", file=stderr)
        exit(2)
    paths = plan_evacuation(lvl)
    for agent_id, path in enumerate(paths):
        print(*path)
        if path[-1] in lvl.scenario.danger:
            print("Agent", agent_id, "could not evacuate. He dead.",
                  file=stderr)


if __name__ == "__main__":
    main()
