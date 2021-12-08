from dataclasses import dataclass

from servey.connector.connector_abc import ConnectorABC
from servey.connector.event.websocket_event_abc import WebsocketEventABC


@dataclass
class Unsubscribe(WebsocketEventABC):
    channel_key: str

    def process(self, connector: ConnectorABC, connection_id: str):
        connector.unsubscribe(connection_id, self.channel_key)
