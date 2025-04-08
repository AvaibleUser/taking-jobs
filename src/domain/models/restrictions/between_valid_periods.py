from attrs import field, frozen

from domain.dtos import Chromosome, Gene
from domain.enums import Period
from domain.models import Restriction


@frozen
class BetweenValidPeriods(Restriction):
    chromosome: Chromosome = field()

    def gene_satisfies(self, gene: Gene) -> bool:
        return gene.period in Period
