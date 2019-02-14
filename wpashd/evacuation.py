import typing
from collections import deque
from graph.nx_graph import NxNode
from wpashd.closest_frontier import ClosestFrontierFinder
from wpashd.rra import RRAHeuristic
from graph.reservation_graph import Reservation, ReservationGraph, ReservationNode
from wpashd.state import State
from wpashd.w_astar import WindowedAstar

class Evacuating(State):
    def __init__(self, agent):
        self.agent = agent
        self.goal = None
        self.retarget()
        self.replan()

    def _rra(self, x, y):
        # RRA is *reversed* so our goal is its start
        if y != self.rra.start:
            raise RuntimeError("Trying to get RRA* heuristic distance to a node different from the goal")
        return self.rra.distance(NxNode(x.pos()))

    def retarget(self):
        self.goal = ClosestFrontierFinder(self.agent.level, NxNode(self.agent.pos.pos())).get_closest_frontier()
        if self.goal is None:
            raise RuntimeError("No safe zone found")
        self.rra = RRAHeuristic(self.agent.level, NxNode(self.agent.pos.pos()), NxNode(self.goal.pos()))

    def pathfind_to(self, goal: ReservationNode) -> typing.List[ReservationNode]:
        search = WindowedAstar(self.agent.reservations, self.agent, self._rra, self.agent.pos, self.goal, self.agent.lookahead)
        if not search.pathfind():
            # closest_frontier finder should either have found a path to safety 
            # and we should be able to find it in spacetime, even if it becomes
            # very long, or we should have caught the problem down in self.retarget()
            raise RuntimeError("Couldn't find way to safety (TODO fix, shouldn't happen)")
        return typing.cast(typing.List[ReservationNode], search.reconstruct_path())

    def replan(self):
        self.agent.cancel_reservations()
        self.agent.next_path = deque(self.pathfind_to(self.goal)[1:])
        self.agent._log(f"Next: {self.agent.next_path}")
        self.agent.reserve_next_path()

    def step(self) -> ReservationNode:
        if len(self.agent.next_path) == self.agent.lookahead // 2 or not self.agent.check_reservations():
            self.replan()
        return self.agent.next_path.popleft()

    def name(self) -> str:
        return "s"