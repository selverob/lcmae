import typing
from random import choice

from .abstract import Evacuating
from evacsim.graph.reservation_graph import ReservationNode


class PanicEvacuation(Evacuating):
    def find_goal(self):
        pass

    def retarget(self):
        pass

    def pathfind(self) -> typing.List[ReservationNode]:
        path = [self.agent.pos]
        while path[-1].t < path[0].t + self.agent.lookahead:
            neighbors = self.neighbors(path[-1])
            if neighbors:
                path.append(choice(neighbors)[0])
            else:
                path.append(path[-1].incremented_t())
        return path

    def neighbors(self, n: ReservationNode) -> typing.List[typing.Tuple[ReservationNode, int]]:
        neighbors = []
        for k in self.agent.reservations.g[n.pos()].keys():
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

    def _reservable_by(self, node: ReservationNode) -> bool:
        reservation = self.agent.reservations.get(node)
        return reservation is None or reservation.agent == self.agent.id or reservation.priority < 2
