from typing import List

from attrs import field, frozen

from domain.dtos import Gene
from utils.toml import define


@define
@frozen
class Chromosome:
    id: int = field()
    generation: int = field()
    score: float | None = field(default=None)
    active: bool = field(default=True)
    genes: List[Gene] | None = field(factory=list, default=None)
