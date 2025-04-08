from dataclasses import dataclass

from domain.enums import Semester
from utils.toml import dict_to_toml


@dataclass(frozen=True)
class Course:
    name: str
    code: int
    degree: str
    semester: Semester
    section: str
    optional: bool

    def __str__(self) -> str:
        return dict_to_toml("course", {
            "name": self.name,
            "code": self.code,
            "degree": self.degree,
            "semester": self.semester,
            "section": self.section,
            "optional": self.optional,
        })
