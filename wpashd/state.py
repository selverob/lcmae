from abc import ABC, abstractmethod
from graph.reservation_graph import ReservationNode

class State(ABC):
    @abstractmethod
    def step(self) -> ReservationNode:
        raise NotImplementedError()

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
