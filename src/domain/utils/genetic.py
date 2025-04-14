from typing import Callable, Iterable

from attrs import define, field

from domain.dtos import Chromosome

Population = Iterable[Chromosome]


@define
class Parents:
    parent1: Chromosome = field()
    parent2: Chromosome = field()


@define
class Parents:
    parent1: Chromosome = field()
    parent2: Chromosome = field()


CrossoverMethod = Callable[[Parents, int], Population]

MutateMethod = Callable[[Chromosome], None]
