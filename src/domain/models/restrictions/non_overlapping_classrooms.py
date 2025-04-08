from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.models import Restriction
from utils.memory import CON


@dataclass(frozen=True)
class NonOverlappingClassrooms(Restriction):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        classroom = self.chromosome.classroom
        period = self.chromosome.period

        classrooms_count = CON.query(
            """
            SELECT COUNT(*)
            FROM chomosome
            WHERE classroom = $classroom
                AND period = $period;
            """,
            params={
                "classroom": classroom,
                "period": period,
            }).first()[0]

        return (classrooms_count < 2) * self._WEIGHT
