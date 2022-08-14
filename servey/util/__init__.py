import re

_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(name: str) -> str:
    return _PATTERN.sub("_", name).lower()
