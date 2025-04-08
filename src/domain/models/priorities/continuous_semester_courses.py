from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.models import Priority
from utils.memory import CON


@dataclass(frozen=True)
class ContinuousSemesterCourses(Priority):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        course = self.chromosome.course
        period = self.chromosome.period

        courses_count = CON.query(
            """
            SELECT COUNT(DISTINCT ch.period)
            FROM course co
                JOIN chromosome ch
                    ON ch.course = co.code
            WHERE co.degree = $degree
                AND co.semester = $semester
                AND (ch.period == $period + 1 OR ch.period == $period - 1);
            """,
            params={
                "degree": course.degree,
                "semester": course.semester,
                "period": period,
            }).first()[0]

        return courses_count * self._WEIGHT
