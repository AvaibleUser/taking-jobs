from random import choices, shuffle
from typing import Iterable

from domain.dtos import Chromosome


def select_elites(population: Iterable[Chromosome]) -> Iterable[Chromosome]:
    return tuple(filter(lambda c: c.score >= 1,
                        sorted(population, key=lambda c: c.score)))


def select_parents(population: Iterable[Chromosome], pool_size: int) -> Iterable[Chromosome]:
    min_score = min(0, map(lambda c: c.score, population))
    probs = tuple(map(lambda c: c.score %
                  (1 if c.score >= 1 else c.score + 1) - min_score, population))
    total_prob = sum(probs)
    probs = map(lambda p: p / total_prob, probs)

    return choices(population, k=pool_size, weights=probs)
