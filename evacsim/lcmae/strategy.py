from abc import ABC, abstractmethod
from evacsim.graph.reservation_graph import ReservationNode


class Strategy(ABC):
    @abstractmethod
    def step(self) -> ReservationNode:
        raise NotImplementedError()

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
