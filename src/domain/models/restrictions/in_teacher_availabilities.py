from dataclasses import dataclass

from domain.dtos import Chromosome
from domain.models import Restriction


@dataclass(frozen=True)
class InTeacherAvailabilities(Restriction):
    chromosome: Chromosome

    def is_satisfied(self) -> float:
        available_courses = self.chromosome.teacher.available_courses
        course = self.chromosome.course.code

        return (course in available_courses) * self._WEIGHT
