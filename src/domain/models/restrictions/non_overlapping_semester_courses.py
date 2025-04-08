from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class NonOverlappingSemesterCourses(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        course = gene.course.code
        period = gene.period

        genes = self.chromosome.genes
        genes = filter(lambda g: g.course.code == course, genes)
        genes = filter(lambda g: g.period == period, genes)

        return len(genes) < 2
