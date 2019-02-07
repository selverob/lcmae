from __future__ import annotations
from graph.interface import Graph, Node
from typing import List, Optional
import networkx as nx

class ReservationNode(Node):
    def __init__(self, orig_id: int, t: int):
        self._pos = orig_id
        self.t = t
    
    def id(self) -> int:
        return self._pos * 10000 + self.t
    
    def pos(self) -> int:
        return self._pos

    def incremented_t(self) -> ReservationNode:
        return ReservationNode(self.pos(), self.t + 1)

class ReservationGraph(Graph[ReservationNode]):
    def __init__(self, underlying_graph: nx.Graph):
        self.g = underlying_graph
        for n in self.g.nodes:
            self.g.nodes[n]["reservations"] = dict()
            self.g.nodes[n]["occupied"] = dict()
    
    def neighbors(self, n: ReservationNode) -> List[ReservationNode]:
        neighbors = []
        for k in self.g[n.pos()].keys():
            rn = ReservationNode(k, n.t + 1)
            if self.reserved_by(rn) is None and self.reserved_by(rn.incremented_t()) is None:
                neighbors.append(rn)
        this_node = n.incremented_t()
        if self.reserved_by(this_node) is None and self.reserved_by(this_node.incremented_t()) is None:
            neighbors.append(this_node)
        return neighbors
  
    def reserved_by(self, n: ReservationNode) -> Optional[int]:
        return self.g.nodes[n.pos()]["reservations"].get(n.t)
    
    def reserve(self, n: ReservationNode, agent: int):
        self.g.nodes[n.pos()]["reservations"][n.t] = agent
    
    def cancel_reservation(self, n: ReservationNode):
        # We cannot be sure cancelled reservation will exist
        # because agents reserve all of their locations for
        # both t and t+1 and so if they're staying in the
        # same node at both t and t+1, they'll try to cancel
        # the reservation for t+1 twice
        self.g.nodes[n.pos()]["reservations"].pop(n.t, None)

    # def occupied_by(self, n: ReservationNode) -> int:
    #     return n.t in self.g.nodes[n.pos()]["occupied"]
    
    # def occupy(self, n: ReservationNode):
    #     self.g.nodes[n.pos()]["occupied"].insert(n.t)