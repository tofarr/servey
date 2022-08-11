from dataclasses import dataclass


@dataclass(frozen=True)
class FixedRateTrigger:
    interval: int
