from typing import Any


def dict_to_toml(type: str, **properties: Any) -> str:
    values_generator = (f"{key}: {value}"
                        for key, value in properties.items()
                        if value is not None)

    return f"[{type}]\n" + "\n".join(values_generator)
