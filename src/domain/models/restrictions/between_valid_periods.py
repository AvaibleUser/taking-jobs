from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.enums import Period
from domain.models import Restriction


@dataclass(frozen=True)
class BetweenValidPeriods(Restriction):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        return (self.chromosome.period in Period) * self._WEIGHT
