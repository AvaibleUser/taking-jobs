from attrs import frozen

from domain.dtos import Gene
from domain.models import Restriction


@frozen
class InTeacherSchedule(Restriction):
    def gene_satisfies(self, gene: Gene) -> bool:
        satisfied = gene.teacher.check_in <= gene.period < gene.teacher.check_out

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
