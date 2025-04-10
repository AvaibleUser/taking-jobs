import attrs
from attrs import field

from domain.dtos import Classroom, Course, Teacher
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
