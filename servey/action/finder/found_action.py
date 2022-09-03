from dataclasses import dataclass
from typing import Callable, Optional, Type

from servey.action.action_meta import ActionMeta


@dataclass
class FoundAction:
    action_meta: ActionMeta
    fn: Callable
    owner: Optional[Type] = None
