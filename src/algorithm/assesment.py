from typing import List

from domain.dtos import Chromosome
from domain.models import Priority, Restriction
from domain.models.priorities import ContinuousSemesterCourses
from domain.models.restrictions import (BetweenValidPeriods,
                                        InTeacherAvailabilities,
                                        InTeacherSchedule,
                                        NonOverlappingClassrooms,
                                        NonOverlappingSemesterCourses,
                                        NonOverlappingTeacherSchedule)

__LIGHT_WEIGHT = 0.5
__HEAVY_WEIGHT = 1.5


def calculate_fitness_score(chromosome: Chromosome) -> float:
    genes = chromosome.genes
    if genes is None:
        chromosome.score = 0
        return 0

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

    chromosome.score = sum(
        __HEAVY_WEIGHT *
        sum(1 if r.gene_satisfies(g) else -1 for r in restrictions) +
        __LIGHT_WEIGHT *
        sum(1 if p.gene_satisfies(g) else -1 for p in priorities)
        for g in genes
    )

    return chromosome.score
