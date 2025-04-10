from typing import Set

from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Priority


@frozen
class ContinuousSemesterCourses(Priority):
    chromosome: Chromosome = field()
    genes_store: Set[int] = field(factory=set)

    def gene_satisfies(self, gene: Gene) -> bool:
        degree = gene.course.degree
        semester = gene.course.semester
        continuous_periods = {gene.period + 1, gene.period - 1}

        genes = self.chromosome.genes
        genes = filter(lambda g: g.course.degree == degree, genes)
        genes = list(filter(lambda g: g.course.semester == semester, genes))

        possible_continuous_courses = len(genes)
        if possible_continuous_courses < 2:
            return True

        genes = filter(lambda g: g.period in continuous_periods, genes)

        satisfied = len(list(genes)) > 0

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
