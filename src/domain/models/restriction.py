from abc import ABC, abstractmethod

from domain.dtos import Gene


class Restriction(ABC):
    @abstractmethod
    def gene_satisfies(self, gene: Gene) -> bool:
        pass
