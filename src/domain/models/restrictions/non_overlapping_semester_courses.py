from typing import Set

from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class NonOverlappingSemesterCourses(Restriction):
    chromosome: Chromosome = field()
    genes_store: Set[int] = field(factory=set)

    def gene_satisfies(self, gene: Gene) -> bool:
        course = gene.course.code
        period = gene.period
        gene_hash = hash((course, period))

        satisfied = gene_hash not in self.genes_store
        self.genes_store.add(gene_hash)

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
