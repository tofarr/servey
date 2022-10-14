from dataclasses import dataclass

from servey.action.trigger.trigger_abc import TriggerABC


@dataclass(frozen=True)
class FixedRateTrigger(TriggerABC):
    interval: int
