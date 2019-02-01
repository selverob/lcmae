from graph.interface import Graph, Node
import networkx as nx
from typing import List

class NxNode(Node):
    def __init__(self, id: int):
        self._id = id

    def id(self) -> int:
        return self._id
    
    def pos(self) -> int:
        return self._id


class NxGraph(Graph):
    def __init__(self, g: nx.Graph):
        self.g = g
    
    def neighbors(self, node: Node) -> List[Node]:
        return [NxNode(k) for k in self.g[node.id()].keys()]