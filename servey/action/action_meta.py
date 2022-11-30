from dataclasses import dataclass
from typing import Tuple

from schemey import Schema

from servey.action.trigger.trigger_abc import TriggerABC
from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)


@dataclass
class ActionMeta:
    name: str
    description: str
    params_schema: Schema
    result_schema: Schema
    access_control: ActionAccessControlABC
    triggers: Tuple[TriggerABC, ...]
    timeout: int = 15
