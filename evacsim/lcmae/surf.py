import typing
from collections import deque
from pqdict import pqdict

from .strategy import Strategy
from evacsim.graph.reservation_graph import ReservationNode, Reservation


class Surfing(Strategy):
    def __init__(self, agent):
        self.agent = agent
        self.lookback = self.agent.lookahead // 2
        self.lookback_set = set()
        self.reservation_len = self.agent.lookahead // 2
        self.replan()

    def pathfind(self) -> typing.Optional[typing.List[ReservationNode]]:
        opened = pqdict({self.agent.pos: 0})
        closed: typing.Set[ReservationNode] = set()
        g_costs = {self.agent.pos: 0.0}
        predecessors: typing.Dict[ReservationNode, ReservationNode] = {}
        previously_reserved = self._previous_reserved()
        agent_t = self.agent.pos.t
        while opened:
            curr = opened.pop()
            closed.add(curr)
            if curr.t == self.agent.pos.t + self.agent.lookahead:
                path = [curr]
                while path[-1] in predecessors:
                    path.append(predecessors[path[-1]])
                path.reverse()
                return path
            # As we go into the future, backpressure decreases, so that
            # it gradually becomes cheaper for agents to stay put
            backpressure = max(1, previously_reserved - (curr.t - agent_t))
            for (n, cost) in self.neighbors(curr, backpressure):
                if n in closed:
                    continue
                considered_g_cost = g_costs[curr] + cost
                if considered_g_cost >= g_costs.get(n, float("nan")):
                    continue
                g_costs[n] = considered_g_cost
                predecessors[n] = curr
                # Hm.
                f_cost = (considered_g_cost + (self.agent.pos.t + self.agent.lookahead - n.t))
                if n not in opened:
                    opened.additem(n, f_cost)
                else:
                    opened[n] = f_cost
        return None

    def neighbors(self, n: ReservationNode, bp_factor: int) -> typing.List[typing.Tuple[ReservationNode, int]]:
        neighbors = []
        for k in self.agent.reservations.g[n.pos()].keys():
            rn = ReservationNode(k, n.t + 1)
            if self._reservable_by(rn) and self._reservable_by(rn.incremented_t()) and self.agent.level.is_safe(rn.pos()):
                cost = 2
                if rn.pos() in self.lookback_set:
                    cost = 3
                neighbors.append((rn, cost))
        this_node = n.incremented_t()
        this_reservable = (self._reservable_by(this_node) and self._reservable_by(this_node.incremented_t()))
        if this_node == ReservationNode(1107, 140):
            self.agent.log("Considering as tn")
        if this_reservable:
            neighbors.append((this_node, 1 * bp_factor))
        else:
            # Agent can always break another agent's reservation of the node
            # they're currently on, but the action is penalized
            neighbors.append((this_node, 4 * bp_factor))
        if self.agent.id == 269 and self.agent.pos.t == 139:
            self.agent.log(neighbors)
        return neighbors

    def _reservable_by(self, node: ReservationNode) -> bool:
        reservation = self.agent.reservations.get(node)
        return reservation is None or reservation.agent == self.agent.id or reservation.priority < 1

    def _previous_reserved(self) -> int:
        reserved = 0
        t = self.agent.pos.t
        for pos in self.agent.taken_path[-(self.lookback + 1):]:
            if self.agent.reservations.get(ReservationNode(pos.pos(), t)) is not None:
                reserved += 1
        return reserved

    def replan(self):
        self.agent.cancel_reservations()
        self.agent.next_path = deque(self.pathfind()[1:])
        self.agent.log(f"bp={self._previous_reserved()} Next: {self.agent.next_path}")
        self.agent.reserve_next_path(priorities=[2] * self.reservation_len + [1] * self.reservation_len)

    def step(self) -> ReservationNode:
        if len(self.agent.next_path) == self.agent.lookahead // 2 or not self.agent.check_reservations():
            self.replan()
        # The high-priority reservation window in agent's future should keep being updated
        # on each move instead of slowly being used-up until the next search.
        self.agent.reservations.reserve(Reservation(self.agent.next_path[self.reservation_len], self.agent.id, 2))
        next_node = self.agent.next_path.popleft()
        self.lookback_set.add(next_node.pos())
        return next_node

    def name(self) -> str:
        return "s"
