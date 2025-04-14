from collections import defaultdict
from typing import Dict, Set

from attrs import field, frozen

from domain.dtos import Gene
from domain.models import Priority


@frozen
class ContinuousSemesterCourses(Priority):
    genes_store: Dict[int, Set[int]] = field(factory=lambda: defaultdict(set))

    def gene_satisfies(self, gene: Gene) -> bool:
        degree = gene.course.degree
        semester = gene.course.semester
        period = gene.period
        actual_course_hash = hash((degree, semester))
        store = self.genes_store[actual_course_hash]

        satisfied = period + 1 in store or period - 1 in store
        if not satisfied:
            gene.failed_in.add(self.__class__.__name__)

        if period not in store:
            store.add(period)

        return satisfied
