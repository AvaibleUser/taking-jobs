from typing import Any

from attrs import asdict


def __dict_to_toml(type: str, **properties: Any) -> str:
    values_generator = (f"{key}: {value}"
                        for key, value in properties.items()
                        if value is not None)

    return f"[{type}]\n" + "\n".join(values_generator)


def define[T](cls: type[T]) -> type[T]:
    cls.__toml__ = lambda self: __dict_to_toml(
        cls.__name__.lower(), asdict(self))
    return cls


def toml[T](cls: type[T]) -> type[T]:
    return cls.__toml__()
