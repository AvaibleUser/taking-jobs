from typing import Callable, Iterable

from attrs import define, field

from domain.dtos import Chromosome

Population = Iterable[Chromosome]


@define
class Parents:
    parent1: Chromosome = field()
    parent2: Chromosome = field()


@define
class Children:
    child1: Chromosome = field()
    child2: Chromosome = field()


@define
class Parents:
    parent1: Chromosome = field()
    parent2: Chromosome = field()


CrossoverMethod = Callable[[Parents], Children]

MutateMethod = Callable[[Chromosome], None]
