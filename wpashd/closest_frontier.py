from typing import cast, Optional, Tuple
from pqdict import pqdict

from astar import AStar
from level import Level
from graph.interface import Node
from graph.nx_graph import NxGraph, NxNode


class ClosestFrontierFinder(AStar):
    def __init__(self, level: Level, agent_pos: NxNode):
        self.level = level
        super().__init__(NxGraph(level.g), self.manhattan_distance, NxNode(0), agent_pos)
        self.opened = pqdict({
            NxNode(node): self.manhattan_distance(agent_pos, NxNode(node)) for node in self.level.frontier})
        self.g_costs = {NxNode(node): 0.0 for node in self.level.frontier}
        self.goal = agent_pos

    def get_closest_frontier(self) -> Optional[Tuple[NxNode, int]]:
        if self.pathfind():
            path = self.reconstruct_path()
            return (cast(NxNode, path[0]), len(path))
        else:
            return None

    def manhattan_distance(self, x: Node, y: Node) -> int:
        x_coords = self.level.id_to_coords(x.pos())
        y_coords = self.level.id_to_coords(y.pos())
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
