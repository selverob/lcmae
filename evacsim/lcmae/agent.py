#! /usr/bin/env python3
from __future__ import annotations
from collections import deque
from sys import stderr
import typing

from evacsim.graph.reservation_graph import ReservationGraph, ReservationNode, Reservation
from evacsim.level import Level
from .strategy import Strategy
from .surf import Surfing


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
        self.strategy: typing.Optional[Strategy] = None

    @property
    def pos(self) -> ReservationNode:
        return self.taken_path[-1]

    def step(self):
        # Initialized here to respect the random
        # agent order in main function
        if self.strategy is None and self.is_safe():
            self.strategy = Surfing(self)
        elif self.strategy is None and not self.is_safe():
            self.strategy = self.evac_class(self)
        elif not isinstance(self.strategy, Surfing) and self.is_safe():
            self.strategy = Surfing(self)
        elif isinstance(self.strategy, Surfing) and not self.is_safe():
            self.strategy = self.evac_class(self)

        self.taken_path.append(self.strategy.step())

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
            s = self.strategy.name() if self.strategy is not None else ""
            print(f"a={self.id}{s} t={self.taken_path[-1].t}: {msg}", file=stderr)
