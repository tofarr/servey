from dataclasses import dataclass


@dataclass(frozen=True)
class WebTrigger:
    is_mutation: bool = True  # Use post requests instead of get requests
