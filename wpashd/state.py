from abc import ABC, abstractmethod
from graph.reservation_graph import ReservationNode

class State:
    @abstractmethod
    def step(self) -> ReservationNode:
        raise NotImplementedError()
