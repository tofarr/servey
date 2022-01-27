from dataclasses import dataclass, field
from typing import List, Optional

from servey.connector.connector_meta import ConnectorMeta
from servey.meta.action_meta import ActionMeta
from servey.meta.publisher_meta import PublisherMeta


@dataclass
class ServiceMeta:
    name: Optional[str] = None  # Overall service name
    description: Optional[str] = None  # Overall service description
    actions: List[ActionMeta] = field(default_factory=tuple)
    publishers: List[PublisherMeta] = field(default_factory=tuple)
    connector_meta: Optional[ConnectorMeta] = None
