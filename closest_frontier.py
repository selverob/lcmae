from typing import Optional
from astar import AStar
from level import Level
from pqdict import pqdict
from graph.interface import Node
from graph.nx_graph import NxGraph, NxNode


class ClosestFrontierFinder(AStar):
    def __init__(self, level: Level, agent_pos: Node):
        self.level = level
        super().__init__(NxGraph(level.g), self.manhattan_distance, NxNode(0), agent_pos)
        self.opened = pqdict({
            NxNode(node): self.manhattan_distance(agent_pos, NxNode(node)) for node in self.level.frontier})
        self.g_costs = {NxNode(node): 0.0 for node in self.level.frontier}
        self.goal = agent_pos

    def get_closest_frontier(self) -> Optional[Node]:
        if self.pathfind():
            return self.reconstruct_path()[0]
        else:
            return None

    def manhattan_distance(self, x: Node, y: Node) -> int:
        x_coords = self.level.id_to_coords(x.pos())
        y_coords = self.level.id_to_coords(y.pos())
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
