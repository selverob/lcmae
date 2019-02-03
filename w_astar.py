from typing import Callable, Dict, List, Set
from pqdict import pqdict
from graph.reservation_graph import ReservationGraph, ReservationNode


class WindowedAstar:
    def __init__(self,
                 g: ReservationGraph,
                 rra: Callable[[ReservationNode, ReservationNode], int],
                 start: ReservationNode,
                 goal: ReservationNode,
                 depth: int):
        self.g = g
        self.rra = rra
        self.start = start
        self.goal = goal
        self.depth = depth
        self.opened = pqdict({start: rra(start, goal)})
        self.closed: Set[ReservationNode] = set()
        self.g_costs = {start: 0.0}
        self.last_node = None
        self.predecessors: Dict[ReservationNode, ReservationNode] = {}

    def pathfind(self) -> bool:
        while len(self.opened) > 0:
            curr = self.opened.pop()
            self.closed.add(curr)
            if curr.t == self.start.t + self.depth:
                self.last_node = curr
                return True
            for n in self.g.neighbors(curr):
                if n in self.closed:
                    continue
                considered_g_cost = self.g_costs[curr] + 1
                if considered_g_cost >= self.g_costs.get(n, float("nan")):
                    continue
                self.g_costs[n] = considered_g_cost
                self.predecessors[n] = curr
                f_cost = (considered_g_cost +
                          self.rra(n, self.goal))
                if n not in self.opened:
                    self.opened.additem(n, f_cost)
                else:
                    self.opened[n] = f_cost
        return False


    def reconstruct_path(self) -> List[ReservationNode]:
        path = [self.last_node]
        while self.predecessors.get(path[-1], None):
            path.append(self.predecessors[path[-1]])
        path.reverse()
        return path
