from dataclasses import dataclass
from typing import Tuple

from schemey import Schema

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.trigger.trigger_abc import TriggerABC


@dataclass
class ActionMeta:
    name: str
    description: str
    params_schema: Schema
    result_schema: Schema
    access_control: ActionAccessControlABC
    triggers: Tuple[TriggerABC, ...]
    timeout: int = 15
