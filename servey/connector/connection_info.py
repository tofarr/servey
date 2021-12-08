from dataclasses import dataclass
from typing import FrozenSet
from uuid import UUID


@dataclass(frozen=True)
class ConnectionInfo:
    id: UUID
    subscribed_channels: FrozenSet[str]
