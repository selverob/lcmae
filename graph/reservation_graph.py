from graph.interface import Graph, Node
from typing import List
import networkx as nx

class ReservationNode(Node):
    def __init__(self, orig_id: int, t: int):
        self._pos = orig_id
        self.t = t
    
    def id(self) -> int:
        return self._pos * 10000 + self.t
    
    def pos(self) -> int:
        return self._pos

class ReservationGraph(Graph[ReservationNode]):
    def __init__(self, underlying_graph: nx.Graph):
        self.g = underlying_graph
        for n in self.g.nodes:
            self.g.nodes[n]["reservations"] = set()
    
    def neighbors(self, n: ReservationNode) -> List[ReservationNode]:
        neighbors = []
        for k in self.g[n.pos()].keys():
            rn = ReservationNode(k, n.t + 1)
            if not self.is_reserved(rn):
                neighbors.append(rn)
        this_node = ReservationNode(n.pos(), n.t + 1)
        if not self.is_reserved(this_node):
            neighbors.append(this_node)
        return neighbors
  
    def is_reserved(self, n: ReservationNode) -> bool:
        return n.t in self.g.nodes[n.pos()]["reservations"]
    
    def reserve(self, n: ReservationNode):
        self.g.nodes[n.pos()]["reservations"].insert(n.t)