from dataclasses import dataclass
from typing import Tuple, Optional

from schemey import Schema

from servey.action.example import Example
from servey.action.trigger.trigger_abc import TriggerABC
from servey.cache_control.cache_control_abc import CacheControlABC
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
    examples: Optional[Tuple[Example, ...]] = None
    cache_control: Optional[CacheControlABC] = None
