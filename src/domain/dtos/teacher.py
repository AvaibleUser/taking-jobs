from typing import List

from attrs import field, frozen

from domain.enums import Period
from utils.toml import define


@define
@frozen
class Teacher:
    name: str = field()
    personal_record: int = field()
    check_in: Period = field()
    check_out: Period = field()
    active: bool = field(default=True)
    available_courses: List[int] = field(factory=list)
