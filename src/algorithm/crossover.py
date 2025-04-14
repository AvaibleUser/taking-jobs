from concurrent.futures import ThreadPoolExecutor as Pool
from functools import partial
from random import randint, shuffle
from typing import Tuple

from domain.dtos import Chromosome, Gene
from domain.utils.genetic import CrossoverMethod, Parents, Population


def uniform_crossover(pair: Parents, generation: int, swap_prob: float = 0.5) -> Population:
    def swap(x: Gene, y: Gene):
        return (y, x) if randint(0, 1) <= swap_prob else (x, y)

    genes1, genes2 = zip(*(swap(g1, g2)
                           for g1, g2 in zip(pair.parent1.genes, pair.parent2.genes)))

    return (Chromosome(generation=generation, genes=genes1),
            Chromosome(generation=generation, genes=genes2))


def crossover(population: Population, crossover_rate: float, swap_prob: float, generation: int, method: CrossoverMethod = uniform_crossover) -> Tuple[Population, Population]:
    parents = list(population)
    shuffle(parents)
    division_point = int(len(parents) * crossover_rate)
    division_point = division_point if division_point % 2 == 0 else division_point - 1
    parents, rest = parents[:division_point], parents[division_point:]
    parents = (Parents(parent1=p1, parent2=p2)
               for p1, p2 in zip(parents[::2], parents[1::2]))

    method = partial(method, generation=generation, swap_prob=swap_prob)

    with Pool() as pool:
        children = pool.map(method, parents)

    children = list(zip(*children))
    children = list(children[0] + children[1])

    return children, rest
