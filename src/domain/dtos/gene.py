from typing import Set

import attrs
from attrs import field

from domain.dtos.classroom import Classroom
from domain.dtos.course import Course
from domain.dtos.teacher import Teacher
from domain.enums import Period
from utils.toml import define


@define
@attrs.define
class Gene:
    id: int = field()
    classroom: Classroom = field()
    course: Course = field()
    teacher: Teacher = field()
    period: Period = field()
    failed_in: Set[int] = field(factory=set)
