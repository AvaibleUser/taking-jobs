from abc import ABC, abstractmethod


class Priority(ABC):
    _WEIGHT = 0.25 / 2

    @abstractmethod
    def is_satisfied(self) -> float:
        pass
