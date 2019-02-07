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

from w_astar import WindowedAstar
from closest_frontier import ClosestFrontierFinder
from graph.nx_graph import NxNode
from graph.reservation_graph import ReservationGraph, ReservationNode
from level import Level
from rra import RRAHeuristic

LOOKAHEAD = 10

class Agent:
    def __init__(self, agent_id: int, level: Level, reservations: ReservationGraph):
        self.id = agent_id
        self.level = level
        self.taken_path = [ReservationNode(level.scenario.agents[agent_id], 0)]
        self.next_path: typing.Deque[ReservationNode] = deque()
        self.reservations = reservations
        self.retarget()

    @property
    def pos(self) -> ReservationNode:
        return self.taken_path[-1]

    def pathfind_to(self, goal: ReservationNode) -> typing.List[ReservationNode]:
        search = WindowedAstar(self.reservations, self._rra, self.pos, self.goal, LOOKAHEAD)
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

    def step(self):
        if len(self.next_path) == 0:
            self.retarget()
            self.reservations.cancel_reservation(self.pos)
            self.next_path = deque(self.pathfind_to(self.goal))
            self._log(f"Next: {self.next_path}")
            self.reserve_next_path()
            self.taken_path.pop()
        if len(self.next_path) == LOOKAHEAD // 2:
            self.cancel_next_path_reservations()
            self.next_path = deque(self.pathfind_to(self.goal)[1:])
            self._log(f"Next: {self.next_path}")
            self.reserve_next_path()
        self.taken_path.append(self.next_path.popleft())

    def is_safe(self) -> bool:
        return not self.level.g.nodes[self.pos]["dangerous"]

    def reserve_next_path(self):
        for node in self.next_path:
            this_r = self.reservations.reserved_by(node)
            if this_r != None and this_r != self.id:
                self._log(f"WARN: Overwriting reservation ({node})")
            next_r = self.reservations.reserved_by(node.incremented_t())
            if next_r != None and next_r != self.id:
                self._log(f"WARN: Overwriting reservation ({node.incremented_t()} - inc)")
            self.reservations.reserve(node, self.id)
            self.reservations.reserve(node.incremented_t(), self.id)
    
    def cancel_next_path_reservations(self):
        for node in self.next_path:
            if self.reservations.reserved_by(node) == self.id:
                self.reservations.cancel_reservation(node)
            next_node = node.incremented_t()
            if self.reservations.reserved_by(next_node) == self.id:
                self.reservations.cancel_reservation(next_node)
    
    def _log(self, msg):
        print(f"a={self.id} t={self.taken_path[-1].t}: {msg}", file=stderr)

def plan_evacuation(level, random_seed=42):
    random.seed(random_seed)
    reservations = ReservationGraph(level.g)
    agents = [Agent(i, level, reservations) for i in range(len(level.scenario.agents))]
    for agent in agents:
        reservations.reserve(agent.pos, agent.id)
    agent_order = list(range(len(agents)))
    deadlock_timer = 0
    # Time is watched independently by agents but this variable makes
    # debugging easier
    t = 0
    while deadlock_timer < 15:
        random.shuffle(agent_order)
        deadlock_timer += 1
        for i in agent_order:
            agents[i].step()
            if len(agents[i].taken_path) < 2 or agents[i].taken_path[-1].pos() != agents[i].taken_path[-2].pos():
                deadlock_timer = 0
        t += 1
    return [list(map(ReservationNode.pos, agent.taken_path)) for agent in agents]


def main():
    map_path, scen_path = argv[1], argv[2]
    lvl = Level(map_path, scen_path)
    for n in lvl.g.nodes:
        lvl.g.nodes[n]["reservations"] = set()
    if len(lvl.frontier) == 0:
        print("No passage to safety exists!", file=stderr)
        exit(2)
    paths = plan_evacuation(lvl)
    for agent_id, path in enumerate(paths):
        num_strings = ["{:02d}".format(n) for n in path]
        print(*num_strings)
        if path[-1] in lvl.scenario.danger:
            print("Agent", agent_id, "could not evacuate. He dead.",
                  file=stderr)


if __name__ == "__main__":
    main()
