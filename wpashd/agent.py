#! /usr/bin/env python3
from __future__ import annotations

# WPASHD - Windowed per-agent Shortest Heurestic Distance
# - Agent uses a heurestic (Manhattan distance) to generate
#   a list of closest safe nodes
# - Using A*, agent finds a path towards the closest one.
#   If that's impossible, it sequentially tries next-best nodes
# - Agent pathfinds to the goal, using WHCA*
#   (follows the planned route and in case of imminent collision, it replans)
# - When the agent is already at the goal, it uses the reservation table to
#   check whether it should make way for incoming agents.
import random
from collections import deque
from pqdict import pqdict
from sys import argv, stderr
import typing

from graph.nx_graph import NxNode
from graph.reservation_graph import ReservationGraph, ReservationNode, Reservation
from level import Level
from wpashd.closest_frontier import ClosestFrontierFinder
from wpashd.rra import RRAHeuristic
from wpashd.w_astar import WindowedAstar

LOOKAHEAD = 10

class Agent:
    def __init__(self, agent_id: int, level: Level, reservations: ReservationGraph):
        self.id = agent_id
        self.level = level
        self.taken_path = [ReservationNode(level.scenario.agents[agent_id], 0)]
        self.next_path: typing.Deque[ReservationNode] = deque()
        self.reservations = reservations
        self._first_step_made = False
        self.retarget()

    @property
    def pos(self) -> ReservationNode:
        return self.taken_path[-1]

    def pathfind_to(self, goal: ReservationNode) -> typing.List[ReservationNode]:
        search = WindowedAstar(self.reservations, self, self._rra, self.pos, self.goal, LOOKAHEAD)
        if not search.pathfind():
            # closest_frontier finder should either have found a path to safety 
            # and we should be able to find it in spacetime, even if it becomes
            # very long, or we should have caught the problem down in self.retarget()
            raise RuntimeError("Couldn't find way to safety (TODO fix, shouldn't happen)")
        return typing.cast(typing.List[ReservationNode], search.reconstruct_path())

    def _rra(self, x, y):
        # RRA is *reversed* so our goal is its start
        if y != self.rra.start:
            raise RuntimeError("Trying to get RRA* heuristic distance to a node different from the goal")
        return self.rra.distance(NxNode(x.pos()))

    def retarget(self):
        self.goal = ClosestFrontierFinder(self.level, NxNode(self.pos.pos())).get_closest_frontier()
        if self.goal is None:
            raise RuntimeError("No safe zone found")
        self.rra = RRAHeuristic(self.level, NxNode(self.pos.pos()), NxNode(self.goal.pos()))

    def replan(self):
        self.cancel_reservations()
        self.next_path = deque(self.pathfind_to(self.goal)[1:])
        self._log(f"Next: {self.next_path}")
        self.reserve_next_path()

    def step(self):
        if not self._first_step_made:
            self._first_step_made = True
            self.retarget()
            self.replan()
        if len(self.next_path) == LOOKAHEAD // 2:
            self.replan()
        if not self.check_reservations():
            self.replan()
        self.taken_path.append(self.next_path.popleft())

    def is_safe(self) -> bool:
        return not self.level.g.nodes[self.pos.pos()]["dangerous"]

    def reserve_next_path(self):
        for node in self.next_path:
            this_r = self.reservations.get(node)
            if this_r is not None and this_r.agent != self.id:
                self._log(f"WARN: Overwriting reservation ({node})")
            next_r = self.reservations.get(node.incremented_t())
            if next_r is not None and next_r.agent != self.id:
                self._log(f"WARN: Overwriting reservation ({node.incremented_t()} - inc)")
            self.reservations.reserve(Reservation(node, self.id, 2))
            self.reservations.reserve(Reservation(node.incremented_t(), self.id, 2))
    
    def cancel_reservations(self):
        for node in self.next_path:
            r = self.reservations.get(node)
            if r is not None and r.agent == self.id:
                self.reservations.cancel_reservation(node)
            next_node = node.incremented_t()
            r = self.reservations.get(next_node)
            if r is not None and r.agent == self.id:
                self.reservations.cancel_reservation(next_node)
    
    def check_reservations(self) -> bool:
        for node in self.next_path:
            res = self.reservations.get(node)
            if res is not None and res.agent != self.id:
                return False
        return True
    
    def _log(self, msg):
        print(f"a={self.id} t={self.taken_path[-1].t}: {msg}", file=stderr)

