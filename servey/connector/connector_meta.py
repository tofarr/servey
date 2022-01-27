from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorMeta:
    url: str
