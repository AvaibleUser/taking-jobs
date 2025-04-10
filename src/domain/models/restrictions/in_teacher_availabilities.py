from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class InTeacherAvailabilities(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        satisfied = gene.course.code in gene.teacher.available_courses

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
