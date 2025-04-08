from abc import ABC, abstractmethod


class Restriction(ABC):
    _WEIGHT = 0.75 / 5

    @abstractmethod
    def is_satisfied(self) -> float:
        pass
