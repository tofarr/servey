from dataclasses import dataclass, field
from typing import List, Optional

from servey.meta.action_meta import ActionMeta


@dataclass
class ServiceMeta:
    name: Optional[str] = None  # Overall service name
    description: Optional[str] = None  # Overall service description
    action_meta: List[ActionMeta] = field(default_factory=list)
