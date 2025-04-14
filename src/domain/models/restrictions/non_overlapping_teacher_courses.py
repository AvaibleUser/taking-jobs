from typing import Set

from attrs import field, frozen

from domain.dtos import Gene
from domain.models import Restriction


@frozen
class NonOverlappingTeacherSchedule(Restriction):
    genes_store: Set[int] = field(factory=set)

    def gene_satisfies(self, gene: Gene) -> bool:
        teacher = gene.teacher.personal_record
        period = gene.period
        gene_hash = hash((teacher, period))

        satisfied = gene_hash not in self.genes_store

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)
        else:
            self.genes_store.add(gene_hash)

        return satisfied
