from typing import List

from attrs import define as attrs
from attrs import field

from domain.dtos.gene import Gene
from utils.toml import define


@define
@attrs
class Chromosome:
    generation: int = field()
    score: float | None = field(default=None)
    genes: List[Gene] = field(factory=list)
