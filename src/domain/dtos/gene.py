from typing import Set

from attrs import define as attrs
from attrs import field

from domain.dtos.classroom import Classroom
from domain.dtos.course import Course
from domain.dtos.teacher import Teacher
from domain.enums import Period
from utils.toml import define


@define
@attrs
class Gene:
    classroom: Classroom = field()
    course: Course = field()
    teacher: Teacher = field()
    period: Period = field()
    failed_in: Set[int] = field(factory=set)

    def __hash__(self):
        return hash((self.classroom.id, self.course.code, self.teacher.personal_record, self.period))
