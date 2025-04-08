from dataclasses import dataclass

from domain.dtos import Classroom, Course, Period, Teacher


@dataclass(frozen=True)
class Chromosome:
    classroom: Classroom
    course: Course
    teacher: Teacher
    period: Period
