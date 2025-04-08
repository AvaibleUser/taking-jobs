from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Priority


@frozen
class ContinuousSemesterCourses(Priority):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        degree = gene.course.degree
        semester = gene.course.semester
        continuous_periods = {gene.period + 1, gene.period - 1}

        genes = self.chromosome.genes
        genes = filter(lambda g: g.course.degree == degree, genes)
        genes = filter(lambda g: g.course.semester == semester, genes)
        genes = filter(lambda g: g.period in continuous_periods, genes)

        return len(genes) > 0
