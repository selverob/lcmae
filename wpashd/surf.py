import typing
from collections import deque, Counter
from pqdict import pqdict

from wpashd.state import State
from graph.reservation_graph import ReservationNode


class Surfing(State):
    def __init__(self, agent):
        self.agent = agent
        self.lookback = self.agent.lookahead // 2
        self.lookback_set = set()
        self.replan()

    def pathfind(self) -> typing.Optional[typing.List[ReservationNode]]:
        opened = pqdict({self.agent.pos: 0})
        closed: typing.Set[ReservationNode] = set()
        g_costs = {self.agent.pos: 0.0}
        predecessors: typing.Dict[ReservationNode, ReservationNode] = {}
        backpressure = self._backpressure()
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
            bp_factor = max(1, backpressure - (curr.t - agent_t))
            for (n, cost) in self.neighbors(curr, bp_factor):
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

    def neighbors(self, n: ReservationNode, cost_factor: int) -> typing.List[typing.Tuple[ReservationNode, int]]:
        neighbors = []
        for k in self.agent.reservations.g[n.pos()].keys():
            rn = ReservationNode(k, n.t + 1)
            if self._reservable_by(rn) and self._reservable_by(rn.incremented_t()):
                cost = 2
                # Going back to danger is heavily penalized
                if not self.agent.level.is_safe(rn.pos()):
                    cost = 4 * cost_factor
                elif rn.pos() in self.lookback_set:
                    cost = 3
                neighbors.append((rn, cost))
        this_node = n.incremented_t()
        this_reservable = (self._reservable_by(this_node) and self._reservable_by(this_node.incremented_t()))
        if this_reservable:
            neighbors.append((this_node, 1 * cost_factor))
        elif self.agent.pos.pos() == this_node.pos():
            # Agent can always break another agent's reservation of the node
            # they're currently on, but the action is penalized
            neighbors.append((this_node, 3 * cost_factor))
        return neighbors

    def _reservable_by(self, node: ReservationNode) -> bool:
        reservation = self.agent.reservations.get(node)
        return reservation is None or reservation.agent == self.agent.id or reservation.priority < 1

    def _backpressure(self) -> int:
        if len(self.agent.taken_path) < self.lookback:
            return 0
        reserved = 0
        t = self.agent.pos.t
        for i in range(1, self.lookback + 1):
            pos = self.agent.taken_path[-i]
            if self.agent.reservations.get(ReservationNode(pos.pos(), t)) is not None:
                reserved += 1
        return reserved

    def replan(self):
        self.agent.cancel_reservations()
        self.agent.next_path = deque(self.pathfind()[1:])
        self.agent.log(f"bp={self._backpressure()} Next: {self.agent.next_path}")
        reservation_len = self.agent.lookahead // 2
        self.agent.reserve_next_path(priorities=[2] * reservation_len + [1] * reservation_len)

    def step(self) -> ReservationNode:
        if len(self.agent.next_path) == self.agent.lookahead // 2 or not self.agent.check_reservations():
            self.replan()
        next_node = self.agent.next_path.popleft()
        # if len(self.lookback_set) == self.lookback:
        #     print(self.agent.taken_path)
        #     print(self.lookback_set)
        #     self.lookback_set.remove(self.agent.taken_path[-self.lookback].pos())
        self.lookback_set.add(next_node.pos())
        return next_node

    def name(self) -> str:
        return "s"
    