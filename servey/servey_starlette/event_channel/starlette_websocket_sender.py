import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.event_channel.websocket.websocket_sender import WebsocketSenderABC, T
from servey.servey_starlette.event_channel.local import get_connections_by_name

LOGGER = logging.getLogger(__name__)


@dataclass
class StarletteWebsocketSender(WebsocketSenderABC[T]):
    """
    Sender for websocket data using starlette. Note: In order to work in a clustered mode,
    the celery websocket sender is required (To broadcast messages to all nodes)
    """

    event_marshaller: MarshallerABC[T]
    event_filter: Optional[EventFilterABC[T]]

    def send(self, channel_name: str, event: T):
        connections = get_connections_by_name().get(channel_name)
        if not connections:
            return
        loop = asyncio.get_event_loop()
        json_event = self.event_marshaller.dump(event)
        for connection in connections.connections:
            # noinspection PyBroadException
            try:
                if not self.event_filter or self.event_filter.should_publish(
                    event, connection.authorization
                ):
                    sending = connection.websocket.send_json(json_event)
                    loop.create_task(sending)
            except Exception:
                LOGGER.exception("failed_to_send_data")
