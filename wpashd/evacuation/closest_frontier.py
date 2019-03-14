from typing import cast, Optional, Tuple
from pqdict import pqdict

from astar import AStar
from level import Level
from manhattan import ManhattanDistanceHeuristic
from graph.nx_graph import NxGraph, NxNode
from .abstract import Evacuating


class ClosestFrontierFinder(AStar):
    def __init__(self, level: Level, agent_pos: NxNode):
        self.level = level
        h = ManhattanDistanceHeuristic(level).manhattan_distance
        super().__init__(NxGraph(level.g), h, NxNode(0), agent_pos)
        self.opened = pqdict({
            NxNode(node): h(agent_pos, NxNode(node)) for node in self.level.frontier})
        self.g_costs = {NxNode(node): 0.0 for node in self.level.frontier}
        self.goal = agent_pos

    def get_closest_frontier(self) -> Optional[Tuple[NxNode, int]]:
        if not self.pathfind():
            return None
        path = self.reconstruct_path()
        return (cast(NxNode, path[0]), len(path))


class ClosestFrontierEvacuation(Evacuating):
    def find_goal(self) -> Tuple[NxNode, int]:
        cf_results = ClosestFrontierFinder(self.agent.level, NxNode(self.agent.pos.pos())).get_closest_frontier()
        if cf_results is None:
            raise RuntimeError("No safe zone found")
        return cf_results
