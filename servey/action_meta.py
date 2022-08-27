from dataclasses import dataclass
from typing import Tuple

from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.trigger.trigger_abc import TriggerABC


@dataclass
class ActionMeta:
    name: str
    description: str
    params_marshaller: MarshallerABC
    params_schema: Schema
    result_marshaller: MarshallerABC
    result_schema: Schema
    access_control: ActionAccessControlABC
    triggers: Tuple[TriggerABC, ...]
    timeout: int = 15
