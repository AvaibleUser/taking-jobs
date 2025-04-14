from concurrent.futures import ThreadPoolExecutor as Pool
from typing import List

from domain.dtos import Chromosome
from domain.models import Priority, Restriction
from domain.models.priorities import ContinuousSemesterCourses
from domain.models.restrictions import (AlreadySelectedClassroom,
                                        BetweenValidPeriods,
                                        InTeacherAvailabilities,
                                        InTeacherSchedule,
                                        NonOverlappingClassrooms,
                                        NonOverlappingSemesterCourses,
                                        NonOverlappingTeacherSchedule)
from domain.utils.genetic import Population

__LIGHT_WEIGHT = 1
__HEAVY_WEIGHT = 10


def __calculate_fitness_score(chromosome: Chromosome) -> Chromosome:
    if chromosome.score is not None:
        return chromosome.score

    restrictions: List[Restriction] = [
        AlreadySelectedClassroom(),
        BetweenValidPeriods(),
        InTeacherAvailabilities(),
        InTeacherSchedule(),
        NonOverlappingClassrooms(),
        NonOverlappingSemesterCourses(),
        NonOverlappingTeacherSchedule(),
    ]
    priorities: List[Priority] = [
        ContinuousSemesterCourses(),
    ]

    genes = chromosome.genes

    total_score = sum(map(
        lambda g:
        __HEAVY_WEIGHT *
        sum(map(lambda r: 1 if r.gene_satisfies(g) else - __LIGHT_WEIGHT - 1, restrictions)) +
        __LIGHT_WEIGHT *
        sum(map(lambda p: 1 if p.gene_satisfies(g) else -1, priorities)),
        genes
    ))
    max_possible_score = (len(restrictions) * __HEAVY_WEIGHT +
                          len(priorities) * __LIGHT_WEIGHT) * len(genes)

    chromosome.score = total_score / max_possible_score

    return chromosome.score


def fitness(population: Population) -> float:
    with Pool() as pool:
        avg_score = sum(pool.map(__calculate_fitness_score,
                        population)) / len(population)

    return avg_score


def check_termination_criteria(
    population: Population,
    generation: int,
    generation_threshold: int,
    fitness_objective: float,
) -> tuple[bool, float]:
    avg_score = fitness(population)

    if generation > generation_threshold:
        return True, avg_score

    stop = any(map(lambda c: c.score >= 0.9975 or (c.generation + 25 >
               generation and c.score >= fitness_objective), population))

    return stop, avg_score
