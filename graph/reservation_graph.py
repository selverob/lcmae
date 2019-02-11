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

    def incremented_t(self, delta = 1) -> ReservationNode:
        return ReservationNode(self.pos(), self.t + delta)

class Reservation:
    def __init__(self, node: ReservationNode, agent: int, priority: int):
        self.node = node
        self.agent = agent
        self.priority = priority

class ReservationGraph():
    def __init__(self, underlying_graph: nx.Graph):
        self.g = underlying_graph
        for n in self.g.nodes:
            self.g.nodes[n]["reservations"] = dict()
            #self.g.nodes[n]["occupied"] = dict()
  
    def get(self, n: ReservationNode) -> Optional[Reservation]:
        return self.g.nodes[n.pos()]["reservations"].get(n.t)
    
    def reserve(self, r: Reservation):
        self.g.nodes[r.node.pos()]["reservations"][r.node.t] = r
    
    def cancel_reservation(self, n: ReservationNode):
        # We cannot be sure cancelled reservation will exist
        # because agents reserve all of their locations for
        # both t and t+1 and so if they're staying in the
        # same node at both t and t+1, they'll try to cancel
        # the reservation for t+1 twice
        self.g.nodes[n.pos()]["reservations"].pop(n.t, None)
