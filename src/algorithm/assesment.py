from typing import List

from algorithm.initialize import generation_threshold
from domain.dtos import Chromosome
from domain.models import Priority, Restriction
from domain.models.priorities import ContinuousSemesterCourses
from domain.models.restrictions import (BetweenValidPeriods,
                                        InTeacherAvailabilities,
                                        InTeacherSchedule,
                                        NonOverlappingClassrooms,
                                        NonOverlappingSemesterCourses,
                                        NonOverlappingTeacherSchedule)
from domain.utils.genetic import Population

__LIGHT_WEIGHT = 0.5
__HEAVY_WEIGHT = 1.5
__first: bool = True
__restrictions: int = 0
__priorities: int = 0


def calculate_fitness_score(chromosome: Chromosome) -> float:
    restrictions: List[Restriction] = [
        BetweenValidPeriods(chromosome),
        InTeacherAvailabilities(chromosome),
        InTeacherSchedule(chromosome),
        NonOverlappingClassrooms(chromosome),
        NonOverlappingSemesterCourses(chromosome),
        NonOverlappingTeacherSchedule(chromosome),
    ]
    priorities: List[Priority] = [
        ContinuousSemesterCourses(chromosome),
    ]
    if __first:
        __first = False
        global __restrictions
        global __priorities
        __restrictions = len(restrictions)
        __priorities = len(priorities)

    genes = chromosome.genes

    total_score = sum(
        __HEAVY_WEIGHT *
        sum(1 if r.gene_satisfies(g) else -1 for r in restrictions) +
        __LIGHT_WEIGHT *
        sum(1 if p.gene_satisfies(g) else -1 for p in priorities)
        for g in genes
    )
    max_possible_score = (len(restrictions) * __HEAVY_WEIGHT +
                          len(priorities) * __LIGHT_WEIGHT) * len(genes)

    chromosome.score = total_score / max_possible_score

    return chromosome.score


def ftiness(population: Population) -> float:
    global __first
    __first = True
    avg_score = sum(map(calculate_fitness_score, population)) / len(population)
    return avg_score


def check_termination_criteria(population: Population, generation_threshold: int = generation_threshold()) -> bool:
    max_generation = max(map(lambda c: c.generation, population))

    if max_generation > generation_threshold:
        return True

    return any(map(lambda c: c.score == 1, population))
