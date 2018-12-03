from typing import Optional
from astar import AStar
from level import Level
from pqdict import pqdict


class ClosestFrontierFinder(AStar):
    def __init__(self, level: Level, agent_pos: int):
        self.level = level
        super().__init__(level.g, self.manhattan_distance, 0, agent_pos)
        self.opened = pqdict({
            node: self.manhattan_distance(agent_pos, node) for node in self.level.frontier})
        self.g_costs = {node: 0.0 for node in self.level.frontier}
        self.goal = agent_pos

    def get_closest_frontier(self) -> Optional[int]:
        if self.pathfind():
            return self.reconstruct_path()[0]
        else:
            return None

    def manhattan_distance(self, x: int, y: int) -> int:
        x_coords = self.level.id_to_coords(x)
        y_coords = self.level.id_to_coords(y)
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
