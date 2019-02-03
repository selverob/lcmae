from astar import AStar
from level import Level
from graph.interface import Node
from graph.nx_graph import NxGraph, NxNode


class RRAHeuristic(AStar):
    def __init__(self, level: Level, position: NxNode, goal: NxNode):
        self.level = level
        super().__init__(NxGraph(level.g), self.manhattan_distance, goal, position)

    def distance(self, position: NxNode) -> int:
        if position == NxNode(89):
            breakpoint
        if position not in self.closed:
            self.goal = position
            if not self.pathfind():
                # This really should not happen due to construction
                # of the rest of algorithms here
                raise RuntimeError("{0} cannot be reached from {1}".format(
                    self.start, position))
        return int(self.g_costs[position])

    def manhattan_distance(self, x: Node, y: Node) -> int:
        x_coords = self.level.id_to_coords(x.pos())
        y_coords = self.level.id_to_coords(y.pos())
        return abs(x_coords[0] - y_coords[0]) + abs(x_coords[1] - y_coords[1])