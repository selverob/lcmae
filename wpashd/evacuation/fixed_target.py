from typing import Tuple
from astar import AStar
from manhattan import ManhattanDistanceHeuristic
from graph.nx_graph import NxGraph, NxNode
from wpashd.agent import Agent
from .abstract import Evacuating

class FixedTargetEvacuation(Evacuating):
    def __init__(self, agent: Agent, target: NxNode):
        self.target_node = target
        self.heuristic = ManhattanDistanceHeuristic(self.agent.level)
        super().__init__(agent)

    def find_goal(self) -> Tuple[NxNode, int]:
        nxg = NxGraph(self.agent.level.g)
        search = AStar(nxg, self.heuristic.manhattan_distance, NxNode(self.agent.pos.pos()), self.target_node)
        search.pathfind()
        return self.target_node, len(search.reconstruct_path())