from abc import ABC, abstractmethod

class BaseSolver(ABC):
    @abstractmethod
    def solve(self, scramble: str) -> str:
        ...
