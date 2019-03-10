from level import Level
from graph.interface import Node

class ManhattanDistanceHeuristic():
    def __init__(self, level: Level):
        self.level = level

    def manhattan_distance(self, x: Node, y: Node) -> int:
        x_coords = self.level.id_to_coords(x.pos())
        y_coords = self.level.id_to_coords(y.pos())
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
