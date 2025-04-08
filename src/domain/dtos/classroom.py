from dataclasses import dataclass

from utils.toml import dict_to_toml


@dataclass(frozen=True)
class Classroom:
    id: int
    name: str
    capacity: int | None = None

    def __str__(self) -> str:
        return dict_to_toml("classroom", {
            "name": self.name,
            "id": self.id,
            "capacity": self.capacity,
        })
