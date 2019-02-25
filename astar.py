from typing import Callable, Dict, List, Set
from pqdict import pqdict
from graph.interface import Graph, Node

class AStar:
    def __init__(self,
                 g: Graph,
                 heuristic: Callable[[Node, Node], int],
                 start: Node,
                 goal: Node):
        self.g = g
        self.heuristic = heuristic
        self.opened = pqdict(
            {start: heuristic(start, goal)})
        self.closed: Set[Node] = set()
        self.g_costs = {start: 0.0}
        self.predecessors: Dict[Node, Node] = {}
        self.start = start
        self.goal = goal

    def pathfind(self) -> bool:
        while self.opened:
            curr = self.opened.pop()
            self.closed.add(curr)
            for n in self.g.neighbors(curr):
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
            if curr.pos() == self.goal.pos():
                return True
        return False


    def reconstruct_path(self) -> List[Node]:
        path = [self.goal]
        while self.predecessors.get(path[-1], None):
            path.append(self.predecessors[path[-1]])
        path.reverse()
        return path
