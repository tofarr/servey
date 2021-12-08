from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey.schema_abc import SchemaABC

from servey.connector.connector_abc import ConnectorABC


T = TypeVar('T')


@dataclass(frozen=True)
class Publisher(Generic[T]):
    """
    An event channel made available in the API. Clients can subscribe to something by name.
    Private channels are unlisted, and disposed of as soon as the last
    """
    name: str
    doc: Optional[str]
    event_marshaller: MarshallerABC[T]
    event_schema: SchemaABC[T]

    def publish(self, event: T, connector: Optional[ConnectorABC] = None):
        if connector is None:
            from servey.servey_context import get_default_servey_context
            connector = get_default_servey_context().connector
        self.event_schema.validate(event)
        dumped = self.event_marshaller.dump(event)
        connector.send(self.name, dumped)
