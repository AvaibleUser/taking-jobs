from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.models import Restriction


@frozen
class InTeacherSchedule(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        teacher = gene.teacher.personal_record
        schedule = {gene.teacher.check_in, gene.teacher.check_out}

        genes = self.chromosome.genes
        genes = filter(lambda g: g.teacher.personal_record == teacher, genes)
        genes = filter(lambda g: g.period in schedule, genes)

        return len(genes) < 1
