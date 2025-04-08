from dataclasses import dataclass

from utils.toml import dict_to_toml


@dataclass(frozen=True)
class Relation:
    teacher: int
    course: int

    def __str__(self) -> str:
        return dict_to_toml("relation", {
            "teacher": self.teacher,
            "course": self.course,
        })


@dataclass(frozen=True)
class Teacher:
    name: str
    personal_record: int
    check_in: int
    check_out: int
    available_courses: list[Relation] | None = None

    def __str__(self) -> str:
        return dict_to_toml("teacher", {
            "name": self.name,
            "personal_record": self.personal_record,
            "check_in": self.check_in,
            "check_out": self.check_out,
        })
