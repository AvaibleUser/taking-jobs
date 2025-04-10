from random import choices

from domain.utils.genetic import Population


def select_elites_deterministic(population: Population, average_score: float) -> Population:
    return list(filter(lambda c: c.score >= (average_score * 2), population))


def select_elites_ranked(population: Population, percent: float = 0.05) -> Population:
    ranked = sorted(population, key=lambda c: c.score, reverse=True)
    return ranked[:int(len(population) * percent)]


def select_parents(population: Population, pool_size: int, average_score: float) -> Population:
    min_score = min(*map(lambda c: c.score, population))
    # probs = tuple(pool.map(lambda c: c.score %
    #               (2 if c.score >= (average_score * 2) else c.score + 1) - min_score, population))
    probs = tuple(map(lambda c: c.score - min_score, population))

    return choices(population, k=pool_size, weights=probs)
