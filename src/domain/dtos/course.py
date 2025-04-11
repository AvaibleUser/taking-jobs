from attrs import field, frozen

from domain.enums import Semester
from utils.toml import define


@define
@frozen
class Course:
    name: str = field()
    code: int = field()
    degree: str = field()
    semester: Semester = field()
    section: str = field()
    optional: bool = field()
    classroom: int | None = field(default=None)
    active: bool = field(default=True)
