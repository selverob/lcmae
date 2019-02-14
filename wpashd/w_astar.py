import typing
from pqdict import pqdict
from graph.reservation_graph import ReservationGraph, ReservationNode


class WindowedAstar:
    def __init__(self,
                 g: ReservationGraph,
                 agent,
                 rra: typing.Callable[[ReservationNode, ReservationNode], int],
                 start: ReservationNode,
                 goal: ReservationNode,
                 depth: int,
                 reservation_priority = 2):
        self.g = g
        self.agent = agent
        self.rra = rra
        self.start = start
        self.goal = goal
        self.depth = depth
        self.opened = pqdict({start: rra(start, goal)})
        self.closed: typing.Set[ReservationNode] = set()
        self.g_costs = {start: 0.0}
        self.last_node: typing.Optional[ReservationNode] = None
        self.predecessors: typing.Dict[ReservationNode, ReservationNode] = {}
        self.priority = reservation_priority

    def pathfind(self) -> bool:
        while len(self.opened) > 0:
            curr = self.opened.pop()
            self.closed.add(curr)
            if curr.t == self.start.t + self.depth:
                self.last_node = curr
                return True
            for (n, cost) in self.neighbors(curr):
                if n in self.closed:
                    continue
                considered_g_cost = self.g_costs[curr] + cost
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

    def neighbors(self, n: ReservationNode) -> typing.List[typing.Tuple[ReservationNode, int]]:
        neighbors = []
        for k in self.g.g[n.pos()].keys():
            rn = ReservationNode(k, n.t + 1)
            if self._reservable_by(rn) and self._reservable_by(rn.incremented_t()):
                neighbors.append((rn, 1))
        this_node = n.incremented_t()
        this_reservable = (self._reservable_by(this_node) and self._reservable_by(this_node.incremented_t()))
        if this_reservable:
            neighbors.append((this_node, 1))
        elif self.agent.pos.pos() == this_node.pos():
            # Agent can always break another agent's reservation of the node
            # they're currently on, but the action is penalized
            neighbors.append((this_node, 2))
        return neighbors

    def reconstruct_path(self) -> typing.List[ReservationNode]:
        path = [self.last_node]
        while path[-1] in self.predecessors:
            path.append(self.predecessors[path[-1]])
        path.reverse()
        return typing.cast(typing.List[ReservationNode], path)

    def _reservable_by(self, node: ReservationNode) -> bool:
        reservation = self.g.get(node)
        return reservation is None or reservation.agent == self.agent.id or reservation.priority < self.priority