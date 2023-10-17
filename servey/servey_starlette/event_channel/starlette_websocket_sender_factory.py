from typing import Optional

from marshy import get_default_context
from schemey import Schema

from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.event_channel.websocket.websocket_sender import WebsocketSenderFactoryABC
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.servey_starlette.event_channel.starlette_websocket_sender import (
    StarletteWebsocketSender,
)


class StarletteWebsocketSenderFactory(WebsocketSenderFactoryABC):
    def create(
        self,
        channel_name: str,
        event_schema: Schema,
        access_control: AccessControlABC = ALLOW_ALL,
        event_filter: Optional[EventFilterABC] = None,
    ) -> Optional[StarletteWebsocketSender]:
        event_marshaller = get_default_context().get_marshaller(
            event_schema.python_type
        )
        return StarletteWebsocketSender(event_marshaller, event_filter)
