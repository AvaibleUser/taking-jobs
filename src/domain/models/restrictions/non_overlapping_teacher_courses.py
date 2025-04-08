from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.models import Restriction
from utils.memory import CON


@dataclass(frozen=True)
class NonOverlappingTeacherSchedule(Restriction):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        teacher = self.chromosome.teacher.personal_record
        period = self.chromosome.period

        teacher_schedule_count = CON.query(
            """
            SELECT COUNT(*)
            FROM chromosome
            WHERE teacher = $teacher
                AND period = $period;
            """,
            params={
                "teacher": teacher,
                "period": period,
            }).first()[0]

        return (teacher_schedule_count < 2) * self._WEIGHT
