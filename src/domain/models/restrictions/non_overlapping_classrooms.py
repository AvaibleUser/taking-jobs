from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class NonOverlappingClassrooms(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        classroom = gene.classroom.id
        period = gene.period

        genes = self.chromosome.genes
        genes = filter(lambda g: g.classroom.id == classroom, genes)
        genes = filter(lambda g: g.period == period, genes)

        return len(genes) < 2
