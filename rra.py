from astar import AStar
from level import Level


class RRAHeuristic(AStar):
    def __init__(self, level: Level, position: int, goal: int):
        self.level = level
        super().__init__(level.g, self.manhattan_distance, goal, position)

    def distance(self, position: int) -> int:
        if position not in self.closed:
            self.goal = position
            if not self.pathfind():
                # This really should not happen due to construction
                # of the rest of algorithms here
                raise RuntimeError("{0} cannot be reached from {1}".format(
                    self.start, position))
        return int(self.g_costs[position])

    def manhattan_distance(self, x: int, y: int) -> int:
        x_coords = self.level.id_to_coords(x)
        y_coords = self.level.id_to_coords(y)
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])
