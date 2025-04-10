from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.enums import Period
from domain.models import Restriction


@frozen
class BetweenValidPeriods(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        satisfied = gene.period in Period and gene.period != Period.TEN_PAST_NINE

        gene.failed_in = set()
        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
