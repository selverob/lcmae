from typing import Tuple

from evacsim.astar import AStar
from evacsim.manhattan import ManhattanDistanceHeuristic
from evacsim.graph.nx_graph import NxGraph, NxNode
from evacsim.lcmae.agent import Agent
from .abstract import Evacuating


class FixedTargetEvacuation(Evacuating):
    def __init__(self, agent: Agent, target: NxNode):
        self.heuristic = ManhattanDistanceHeuristic(agent.level)
        self.target_node = target
        super().__init__(agent)

    def find_goal(self) -> Tuple[NxNode, int]:
        nxg = NxGraph(self.agent.level.g)
        search = AStar(nxg, self.heuristic.manhattan_distance, NxNode(self.agent.pos.pos()), self.target_node)
        search.pathfind()
        return self.target_node, len(search.reconstruct_path())
