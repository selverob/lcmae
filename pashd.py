#! /usr/bin/env python3


# Abandoned attempt, unfortunately


# PASHD - Per-agent Shortest Heurestic Distance
# - Agent uses a heurestic (Manhattan distance) to generate
#   a list of closest safe nodes
# - Using A*, agent finds a path towards the closest one.
#   If that's impossible, it sequentially tries next-best nodes
# - Agent pathfinds to the goal, using LRA*
#   (follows the planned route and in case of imminent collision, it replans)
# - If the goal is already occupied, algorithm begins again,
#   considering agent's current position as the start

# Agent state and nudging
# There are two variables affecting agent's behavior - `free` and `safe`
# - `free` indicates whether the agent is waiting on some other agent's action
#   It is true when the agent is not waiting on anything.
# - `safe` indicates whether the agent is currently standing on a safe node
# Agent's behavior depending on these two variables
# - free, safe - agent just waits on its position, if it gets nudged, it moves
#   to another position. If it receives multiple nudges, it moves the respective
#   number of nodes..
# - free, not safe - agent has a path planned. Tries to follow it. 
#   When it collides with another free, unsafe agent, it retargets/replans
#   When it collides with a free, safe agent, it sends a nudge request and 
#   gets blocked.
#   When it collides with a blocked, safe agent, it sends a nudge request 
#   and gets blocked.
#   When it collides with a blocked, unsafe agent, it tries to retarget. If
#   retargeting returns a the same goal, it sends a nudge to the agent waiting
#   on the field. If not, it reroutes to a different goal.
# - not free, safe - waits until a field it can move into becomes free
# - not free, not safe - the same

import random
from collections import deque
from enum import Enum, auto
from level import Level
from pqdict import pqdict
from sys import argv, stderr
from typing import Dict, List, Optional


class AgentState(Enum):
    EVACUATING = auto()
    FREE = auto()
    BLOCKED = auto()


class Agent:
    def __init__(self, agent_id: int, level: Level):
        self.id = agent_id
        self.level = level
        self.taken_path = [level.scenario.agents[agent_id]]
        self.state = AgentState.EVACUATING if not self.is_safe else AgentState.FREE
        self.nudges: List[int] = []
        self.retarget()

    @property
    def pos(self) -> int:
        return self.taken_path[-1]

    def retarget(self):
        self.next_path_idx = 1
        self.future_path = None
        goal_candidates = map(
            lambda x: (x, self.manhattan_distance(self.pos, x)),
            self.level.frontier)
        for candidate, _ in sorted(goal_candidates, key=lambda x: x[1]):
            path = self.pathfind_to(candidate)
            if path:
                self.future_path = deque(path)
                return

    def pathfind_to(self,
                    goal: int) -> Optional[List[int]]:
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
                if first_move and self._check_occupied(n):
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

    def wait(self) -> int:
        self._occupy(self.pos)
        self.taken_path.append(self.pos)
        return self.pos

    def nudge(self, t: int) -> bool:
        print("N", self.id, self.time, t, file=stderr)
        s = [self.pos]
        dists = {self.pos: 0}
        while len(s) > 0:
            node = s.pop()
            dist = dists[node]
            if dist == self.nudge_factor:
                path = self.pathfind_to(node)
                if path:
                    self.future_path = deque(path)
                    return self.move(t)
            for n in self.level.g[node].keys():
                if not self.level.g.nodes[n]["dangerous"]:
                    s.append(n)
                    dists[n] = dist + 1
        return self.move(t)

    def has_path(self):
        return self.future_path is not None

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

    def is_safe(self) -> bool:
        return not self.level.g.nodes[self.pos]["dangerous"]


    """
    def move(self, t) -> bool:
        print(self.id, self.time, t, file=stderr)
        if self.time > t:
            # A move was already performed by us
            # so let's not do anything
            return False
        if (self.future_path is None or len(self.future_path) == 0) and self.is_safe():
            self.wait()
            return False
        next_move = self.future_path[0]
        if self._check_occupied(next_move):
            occupier = self._occupying_agent(next_move)
            if occupier.is_safe():
                if not occupier.nudge(t):
                    self.wait()
                    return True
                else:
                    return self.move(t)
            else:
                self.retarget()
            return self.move(t)
        self._occupy(next_move)
        self.taken_path.append(self.future_path.popleft())
        return True
    """
    def _check_occupied(self, node: int) -> bool:
        if "occupation" in self.level.g.nodes[node]:
            agent, time = self.level.g.nodes[node]["occupation"]
            return agent.id != self.id and time >= self.time - 1
        return False

    def _occupying_agent(self, node: int):
        return self.level.g.nodes[node]["occupation"][0]

    def _occupy(self, node: int):
        assert(not self._check_occupied(node))
        self.level.g.nodes[node]["occupation"] = (self, self.time + 1)


def plan_evacuation(level, random_seed=42):
    random.seed(random_seed)
    agents = [Agent(i, level) for i in range(len(level.scenario.agents))]
    agent_order = list(range(len(agents)))
    finished = False
    t = 1
    while not finished:
        random.shuffle(agent_order)
        finished = True
        for i in agent_order:
            if agents[i].move(t):
                finished = False
        t += 1
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
