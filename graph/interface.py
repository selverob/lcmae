from abc import ABC, abstractmethod
from typing import List

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

class Graph(ABC):
    @abstractmethod
    def neighbors(self, node: Node) -> List[Node]:
        raise NotImplementedError()