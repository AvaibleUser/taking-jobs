from attrs import field, frozen

from utils.toml import define


@define
@frozen
class Classroom:
    id: int = field()
    name: str = field()
    capacity: int | None = field(default=None)
