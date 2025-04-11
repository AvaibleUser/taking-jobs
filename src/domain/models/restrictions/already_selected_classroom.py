from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class AlreadySelectedClassroom(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        classroom = gene.course.classroom
        satisfied = classroom is None or classroom == gene.classroom.id

        gene.failed_in = set()
        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
