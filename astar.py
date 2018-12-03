from typing import Callable, Dict, List, Set
from pqdict import pqdict
import networkx as nx


class AStar:
    def __init__(self,
                 g: nx.Graph,
                 heuristic: Callable[[int, int], int],
                 start: int,
                 goal: int):
        self.g = g
        self.heuristic = heuristic
        self.opened = pqdict(
            {start: heuristic(start, goal)})
        self.closed: Set[int] = set()
        self.g_costs = {start: 0.0}
        self.predecessors: Dict[int, int] = {}
        self.start = start
        self.goal = goal

    def pathfind(self) -> bool:
        while len(self.opened) > 0:
            curr = self.opened.pop()
            self.closed.add(curr)
            if curr == self.goal:
                return True
            for n in self.g[curr].keys():
                if n in self.closed:
                    continue
                considered_g_cost = self.g_costs[curr] + 1
                if considered_g_cost >= self.g_costs.get(n, float("nan")):
                    continue
                self.g_costs[n] = considered_g_cost
                self.predecessors[n] = curr
                f_cost = (considered_g_cost +
                          self.heuristic(n, self.goal))
                if n not in self.opened:
                    self.opened.additem(n, f_cost)
                else:
                    self.opened[n] = f_cost
        return False

    def reconstruct_path(self) -> List[int]:
        path = [self.goal]
        while self.predecessors.get(path[-1], None):
            path.append(self.predecessors[path[-1]])
        path.reverse()
        return path
