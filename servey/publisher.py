from dataclasses import dataclass
from typing import Optional, Generic, TypeVar

from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey.schema_abc import SchemaABC

from servey.connector.connector_abc import ConnectorABC
from servey.meta.publisher_meta import PublisherMeta

T = TypeVar('T')


@dataclass(frozen=True)
class Publisher(Generic[T]):
    name: str
    doc: Optional[str]
    event_marshaller: MarshallerABC[T]
    event_schema: SchemaABC[T]

    def publish(self, event: T, sub_channel_name: Optional[str] = None, connector: Optional[ConnectorABC] = None):
        dumped = self.event_marshaller.dump(event)
        channel_key = self.name
        if sub_channel_name:
            channel_key = f"{self.name}/{sub_channel_name}"
        if connector is None:
            from servey.servey_context import get_default_servey_context
            connector = get_default_servey_context().connector
        connector.send(channel_key, dumped)

    def get_meta(self) -> PublisherMeta:
        return PublisherMeta(self.name, self.doc, self.event_schema)


