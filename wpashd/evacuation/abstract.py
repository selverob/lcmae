import typing
from abc import ABC, abstractmethod
from collections import deque
from graph.nx_graph import NxNode
from graph.reservation_graph import ReservationNode
from wpashd.rra import RRAHeuristic
from wpashd.state import State
from wpashd.w_astar import WindowedAstar

class Evacuating(State, ABC):
    def __init__(self, agent):
        self.agent = agent
        self.goal = None
        self.distance_with_goal = 0
        self.distance_to_goal = 0
        self.retarget()
        self.replan()

    def _rra(self, x, y):
        # RRA is *reversed* so our goal is its start
        if y != self.rra.start:
            raise RuntimeError("Trying to get RRA* heuristic distance to a node different from the goal")
        return self.rra.distance(NxNode(x.pos()))

    @abstractmethod
    def find_goal(self) -> typing.Tuple[NxNode, int]:
        raise NotImplementedError()

    def retarget(self):
        self.goal, self.distance_to_goal = self.find_goal()
        self.rra = RRAHeuristic(self.agent.level, NxNode(self.agent.pos.pos()), NxNode(self.goal.pos()))

    def pathfind(self) -> typing.List[ReservationNode]:
        search = WindowedAstar(self.agent.reservations, self.agent, self._rra, self.agent.pos, self.goal, self.agent.lookahead)
        if not search.pathfind():
            # closest_frontier finder should either have found a path to safety
            # and we should be able to find it in spacetime, even if it becomes
            # very long, or we should have caught the problem down in self.retarget()
            raise RuntimeError("Couldn't find way to safety (TODO fix, shouldn't happen)")
        return typing.cast(typing.List[ReservationNode], search.reconstruct_path())

    def replan(self):
        self.agent.cancel_reservations()
        self.agent.next_path = deque(self.pathfind()[1:])
        self.agent.log(f"Next: {self.agent.next_path}")
        self.agent.reserve_next_path()

    def step(self) -> ReservationNode:
        if len(self.agent.next_path) == self.agent.lookahead // 2 or not self.agent.check_reservations():
            self.replan()
        self.distance_with_goal += 1
        return self.agent.next_path.popleft()

    def name(self) -> str:
        return "e"
