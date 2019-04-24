from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

N = TypeVar("N")


class Node(ABC):
    @abstractmethod
    def id(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def pos(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other):
        return self.id() == other.id()

    def __hash__(self):
        return self.id()

    def __repr__(self):
        return f"Node({self.id()})"


class Graph(Generic[N], ABC):
    @abstractmethod
    def neighbors(self, node: N) -> List[N]:
        raise NotImplementedError()
