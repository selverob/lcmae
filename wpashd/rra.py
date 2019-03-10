from astar import AStar
from level import Level
from manhattan import ManhattanDistanceHeuristic
from graph.nx_graph import NxGraph, NxNode


class RRAHeuristic(AStar):
    def __init__(self, level: Level, position: NxNode, goal: NxNode):
        self.level = level
        super().__init__(NxGraph(level.g), ManhattanDistanceHeuristic(level).manhattan_distance, goal, position)

    def distance(self, position: NxNode) -> int:
        if position not in self.closed:
            self.goal = position
            if not self.pathfind():
                # This really should not happen due to construction
                # of the rest of algorithms here
                raise RuntimeError("{0} cannot be reached from {1}".format(
                    self.start, position))
        return int(self.g_costs[position])
