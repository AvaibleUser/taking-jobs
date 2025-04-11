from functools import partial
from random import randint, shuffle
from typing import Tuple

import duckdb as dd

from domain.dtos import Chromosome, Gene
from domain.utils.genetic import CrossoverMethod, Parents, Population


def uniform_crossover(pair: Parents, generation: int, swap_prob: float = 0.5) -> Population:
    def swap(x: Gene, y: Gene):
        return (y, x) if randint(0, 1) < swap_prob else (x, y)

    genes1, genes2 = zip(*(swap(g1, g2)
                           for g1, g2 in zip(pair.parent1.genes, pair.parent2.genes)))

    generation = pair.parent1.generation + 1
    dd.executemany(
        "INSERT INTO chromosome (generation, parent1, parent2) VALUES (?, ?, ?)",
        [[generation, pair.parent1.id, pair.parent2.id], [generation, pair.parent2.id, pair.parent1.id]])

    child1_id = dd.sql("SELECT MAX(id) FROM chromosome").fetchall()[0][0]
    child2_id = child1_id - 1

    dd.executemany(
        "INSERT INTO gene (classroom, course, teacher, period) VALUES (?, ?, ?, ?)",
        [(g.classroom.id, g.course.code, g.teacher.personal_record, g.period) for g in genes1])

    dd.execute(
        "INSERT INTO chromosome_gene SELECT ? AS chromosome, id AS gene FROM gene g ORDER BY id DESC LIMIT ?",
        (child1_id, len(genes1)))

    dd.executemany(
        "INSERT INTO gene (classroom, course, teacher, period) VALUES (?, ?, ?, ?)",
        [(g.classroom.id, g.course.code, g.teacher.personal_record, g.period) for g in genes2])

    dd.execute(
        "INSERT INTO chromosome_gene SELECT ? AS chromosome, id AS gene FROM gene g ORDER BY id DESC LIMIT ?",
        (child2_id, len(genes2)))

    genes1_df = dd.sql(
        "SELECT g.id FROM gene g JOIN chromosome_gene cg ON g.id = cg.gene WHERE cg.chromosome = ? ORDER BY course",
        params=[child1_id]).to_df()
    genes1 = list(Gene(id, gene.classroom, gene.course, gene.teacher, gene.period)
                  for id, gene in zip(genes1_df.id.to_list(), genes1))

    genes2_df = dd.sql(
        "SELECT g.id FROM gene g JOIN chromosome_gene cg ON g.id = cg.gene WHERE cg.chromosome = ? ORDER BY course",
        params=[child2_id]).to_df()
    genes2 = list(Gene(id, gene.classroom, gene.course, gene.teacher, gene.period)
                  for id, gene in zip(genes2_df.id.to_list(), genes2))

    return (Chromosome(id=child1_id, generation=generation, genes=genes1),
            Chromosome(id=child2_id, generation=generation, genes=genes2))


def crossover(population: Population, crossover_rate: float, generation: int, method: CrossoverMethod = uniform_crossover) -> Tuple[Population, Population]:
    parents = list(population)
    shuffle(parents)
    division_point = int(len(parents) * crossover_rate)
    division_point = division_point if division_point % 2 == 0 else division_point - 1
    parents, rest = parents[:division_point], parents[division_point:]
    parents = (Parents(parent1=p1, parent2=p2)
               for p1, p2 in zip(parents[::2], parents[1::2]))

    method = partial(method, generation=generation)
    dd.begin()
    children = map(method, parents)
    children = list(zip(*children))
    children = list(children[0] + children[1])
    dd.commit()

    return children, rest
