from random import randint, shuffle
from typing import Tuple

import duckdb as dd

from algorithm.initialize import crossover_rate
from domain.dtos import Chromosome, Gene
from domain.utils.genetic import Children, CrossoverMethod, Parents, Population


def uniform_crossover(pair: Parents, swap_prob: float = 0.5) -> Children:
    def swap(x: Gene, y: Gene):
        return (y, x) if randint(0, 1) < swap_prob else (x, y)

    genes1, genes2 = zip(*(swap(g1, g2)
                           for g1, g2 in zip(pair.parent1.genes, pair.parent2.genes)))

    generation = pair.parent1.generation + 1
    dd.executemany(
        "INSERT INTO chromosome (generation, parent1, parent2) VALUES (?, ?, ?)",
        [[generation, pair.parent1, pair.parent2], [generation, pair.parent2, pair.parent1]])

    child1_id = dd.sql("SELECT MAX(id) FROM chromosome").first()[0]
    child2_id = child1_id - 1

    dd.executemany(
        """
        INSERT INTO gene (classroom, course, teacher, period) VALUES (?, ?, ?, ?);
        INSERT INTO chromosome_gene (chromosome, gene) SELECT ?, MAX(id) FROM gene;
        """,
        [(g.classroom, g.course, g.teacher, g.period, child1_id) for g in genes1].extend(
            (g.classroom, g.course, g.teacher, g.period, child2_id) for g in genes2))

    genes1_df = dd.sql(
        "SELECT * FROM gene WHERE chromosome = ?", child1_id).to_df()
    genes1 = (Gene(**row) for row in genes1_df.to_dict("records"))

    genes2_df = dd.sql(
        "SELECT * FROM gene WHERE chromosome = ?", child2_id).to_df()
    genes2 = (Gene(**row) for row in genes2_df.to_dict("records"))

    return Children(child1=Chromosome(id=child1_id, generation=generation, genes=genes1),
                    child2=Chromosome(id=child2_id, generation=generation, genes=genes2))


def crossover(population: Population, crossover_rate: float = crossover_rate(), method: CrossoverMethod = uniform_crossover) -> Tuple[Population, Population]:
    parents = list(population)
    shuffle(parents)
    division_point = int(len(parents) * crossover_rate)
    division_point = division_point if division_point % 2 == 0 else division_point - 1
    parents, rest = parents[:division_point], parents[division_point:]
    parents = (Parents(parent1=p1, parent2=p2)
               for p1, p2 in zip(parents[::2], parents[1::2]))

    return map(method, parents), rest
