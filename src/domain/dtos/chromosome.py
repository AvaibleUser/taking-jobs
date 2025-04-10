from typing import List

import attrs
from attrs import field

from domain.dtos.gene import Gene
from utils.toml import define


@define
@attrs.define
class Chromosome:
    id: int = field()
    generation: int = field()
    score: float = field(default=0)
    active: bool = field(default=True)
    genes: List[Gene] = field(factory=list)
