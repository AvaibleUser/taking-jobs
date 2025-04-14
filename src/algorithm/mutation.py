from concurrent.futures import ThreadPoolExecutor as Pool
from functools import partial
from random import choice, sample

from domain.dtos import Chromosome, Gene
from domain.utils.genetic import CrossoverMethod, Population


def mutate_by_inversion(chromosome: Chromosome, generation: int, inversion_rate: float = 0.10) -> Chromosome:
    ordered_genes = list(chromosome.genes)

    def invert(i: Gene, j: Gene):
        x = ordered_genes[i]
        y = ordered_genes[j]
        x = Gene(x.classroom, x.course, x.teacher, x.period)
        y = Gene(y.classroom, y.course, y.teacher, y.period)

        attr_to_invert = choice(range(3))

        match attr_to_invert:
            case 0:
                x.teacher, y.teacher = y.teacher, x.teacher
            case 1:
                x.classroom, y.classroom = y.classroom, x.classroom
            case 2:
                x.period, y.period = y.period, x.period

        ordered_genes[i] = x
        ordered_genes[j] = y

    inversion_amount = max(2, int(len(ordered_genes) * inversion_rate))
    inversion_amount = inversion_amount if inversion_amount % 2 == 0 else inversion_amount - 1
    genes_to_invert = sample(range(len(ordered_genes)), k=inversion_amount)
    any(invert(i, j)
        for i, j in zip(genes_to_invert[::2], genes_to_invert[1::2]))

    return Chromosome(generation=generation, genes=ordered_genes)


def mutate(population: Population, mutation_rate: float, inversion_rate: float, generation: int, method: CrossoverMethod = mutate_by_inversion) -> Population:
    chromosomes_to_mutate = sample(
        population, k=max(1, int(len(population) * mutation_rate)))
    method = partial(method, generation=generation,
                     inversion_rate=inversion_rate)
    with Pool() as pool:
        return list(pool.map(method, chromosomes_to_mutate))
