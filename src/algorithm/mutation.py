from random import randint, sample

from attrs import astuple
import duckdb as dd

from domain.dtos import Chromosome, Gene
from domain.utils.genetic import CrossoverMethod, Population


def mutate_by_inversion(chromosome: Chromosome, inversion_rate: float = 0.10) -> None:
    def invert(x: Gene, y: Gene):
        attr_to_invert = randint(0, 2)

        match attr_to_invert:
            case 0:
                x.teacher, y.teacher = y.teacher, x.teacher
            case 1:
                x.classroom, y.classroom = y.classroom, x.classroom
            case 2:
                x.period, y.period = y.period, x.period

        return x, y

    inversion_amount = max(2, int(len(chromosome.genes) * inversion_rate))
    inversion_amount = inversion_amount if inversion_amount % 2 == 0 else inversion_amount - 1
    genes_to_invert = sample(chromosome.genes, k=inversion_amount)
    genes = list(zip(*(invert(g1, g2)
                       for g1, g2 in zip(genes_to_invert[::2], genes_to_invert[1::2]))))
    genes = list(genes[0] + genes[1])

    dd.executemany(
        "UPDATE gene SET teacher = ?, classroom = ?, period = ? WHERE id = ?",
        ((g.teacher.personal_record, g.classroom.id, g.period, g.id) for g in genes))


def mutate(population: Population, mutation_rate: float, method: CrossoverMethod = mutate_by_inversion) -> None:
    chromosomes_to_mutate = sample(
        population, k=max(1, int(len(population) * mutation_rate)))
    any(map(method, chromosomes_to_mutate))
