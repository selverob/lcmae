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
from collections import deque
from sys import stderr
import typing

from graph.reservation_graph import ReservationGraph, ReservationNode, Reservation
from level import Level
from wpashd.state import State
from wpashd.surf import Surfing

class Agent:
    def __init__(self, agent_id: int, level: Level, reservations: ReservationGraph, evacuation_class, debug=True):
        self.id = agent_id
        self.lookahead = 10
        self.level = level
        self.next_path: typing.Deque[ReservationNode] = deque()
        self.taken_path = [ReservationNode(level.scenario.agents[agent_id].origin, 0)]
        self.reservations = reservations
        self.evac_class = evacuation_class
        self.debug = debug
        # Initialized in step()
        self.state: typing.Optional[State] = None

    @property
    def pos(self) -> ReservationNode:
        return self.taken_path[-1]

    def step(self):
        # Initialized here to respect the random
        # agent order in main function
        if self.state is None and self.is_safe():
            self.state = Surfing(self)
        elif self.state is None and not self.is_safe():
            self.state = self.evac_class(self)
        elif isinstance(self.state, self.evac_class) and self.is_safe():
            self.state = Surfing(self)
        elif isinstance(self.state, Surfing) and not self.is_safe():
            self.state = self.evac_class(self)

        self.taken_path.append(self.state.step())

    def is_safe(self) -> bool:
        return self.level.is_safe(self.pos.pos())

    def reserve_next_path(self, priorities=[]):
        for i, node in enumerate(self.next_path):
            priority = priorities[i] if len(priorities) > i else 2
            this_r = self.reservations.get(node)
            if this_r is not None and this_r.agent != self.id and this_r.priority >= priority:
                self.log(f"WARN: Overwriting reservation ({node})")
            next_r = self.reservations.get(node.incremented_t())
            if next_r is not None and next_r.agent != self.id and next_r.priority >= priority:
                self.log(f"WARN: Overwriting reservation ({node.incremented_t()} - inc)")
            self.reservations.reserve(Reservation(node, self.id, priority))
            self.reservations.reserve(Reservation(node.incremented_t(), self.id, priority))

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

    def log(self, msg):
        if self.debug:
            s = self.state.name() if self.state is not None else ""
            print(f"a={self.id}{s} t={self.taken_path[-1].t}: {msg}", file=stderr)
