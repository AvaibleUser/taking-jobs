from random import choices

from domain.utils.genetic import Population


def select_elites(population: Population) -> Population:
    return tuple(filter(lambda c: c.score >= 1,
                        sorted(population, key=lambda c: c.score)))


def select_parents(population: Population, pool_size: int) -> Population:
    min_score = min(0, map(lambda c: c.score, population))
    probs = tuple(map(lambda c: c.score %
                  (1 if c.score >= 1 else c.score + 1) - min_score, population))
    total_prob = sum(probs)
    probs = map(lambda p: p / total_prob, probs)

    return choices(population, k=pool_size, weights=probs)
