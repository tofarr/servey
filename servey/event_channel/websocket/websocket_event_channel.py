from dataclasses import dataclass
from typing import Optional, Type

from marshy.factory.impl_marshaller_factory import get_impls
from schemey import schema_from_type, Schema

from servey.errors import ServeyError
from servey.event_channel.event_channel_abc import EventChannelABC, T
from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.event_channel.websocket.websocket_sender import (
    WebsocketSenderABC,
    WebsocketSenderFactoryABC,
)
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL


@dataclass(frozen=True)
class WebsocketEventChannel(EventChannelABC[T]):
    """
    Channel which passes an event_channel to a web socket
    """

    name: str
    event_schema: Schema
    access_control: AccessControlABC
    event_filter: EventFilterABC
    websocket_sender: WebsocketSenderABC

    def publish(self, event: T):
        self.websocket_sender.send(self.name, event)


def websocket_event_channel(
    name: str,
    event_type: Type,
    access_control: AccessControlABC = ALLOW_ALL,
    event_filter: Optional[EventFilterABC] = None,
) -> WebsocketEventChannel:
    schema = schema_from_type(event_type)
    factories = [impl() for impl in get_impls(WebsocketSenderFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    for factory in factories:
        websocket_sender = factory.create(name, schema, event_filter)
        if websocket_sender:
            return WebsocketEventChannel(
                name, schema, access_control, event_filter, websocket_sender
            )
    raise ServeyError(f"no_sender_for_channel:{name}")
