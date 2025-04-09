from attrs import field, frozen

from domain.dtos import Classroom, Course, Teacher
from domain.enums import Period
from utils.toml import define


@define
@frozen
class Gene:
    id: int = field()
    classroom: Classroom = field()
    course: Course = field()
    teacher: Teacher = field()
    period: Period = field()
