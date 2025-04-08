from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.models import Restriction
from utils.memory import CON


@dataclass(frozen=True)
class NonOverlappingSemesterCourses(Restriction):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        course = self.chromosome.course

        if course.optional:
            return self._WEIGHT

        courses_count = CON.query(
            """
            SELECT COUNT(*)
            FROM course
            WHERE code = $code
                AND degree = $degree
                AND semester = $semester
                AND section != $section
                AND optional = FALSE
                AND active = TRUE;
            """,
            params={
                "code": course.code,
                "degree": course.degree,
                "semester": course.semester,
                "section": course.section,
            }).first()[0]

        return (courses_count < 2) * self._WEIGHT
