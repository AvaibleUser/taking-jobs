from attrs import frozen

from domain.dtos import Gene
from domain.enums import Period
from domain.models import Restriction


@frozen
class BetweenValidPeriods(Restriction):
    def gene_satisfies(self, gene: Gene) -> bool:
        satisfied = gene.period in Period and gene.period != Period.TEN_PAST_NINE

        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        return satisfied
