import asyncio
from dataclasses import dataclass, field
import json
import logging
from typing import List, Any, Set, Iterator, Optional
from uuid import UUID, uuid4

from marshy import ExternalType, get_default_context
import websockets
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.connector.connection_info import ConnectionInfo
from servey.connector.connector_abc import ConnectorABC
from threading import Lock

from servey.connector.event.websocket_event_abc import WebsocketEventABC

logger = logging.getLogger(__name__)


@dataclass
class _Connection:
    websocket: Any
    id: UUID = field(default_factory=uuid4)
    channel_keys: Set[str] = field(default_factory=set)

    def send(self, event: ExternalType):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'connection_send:{self.id}:{event}')
        event_str = json.dumps(event)
        self.websocket.send(event_str)


def received_event_marshaller():
    return get_default_context().get_marshaller(WebsocketEventABC)


@dataclass(frozen=True)
class SingleNodeWebsocketConnector(ConnectorABC):
    """
    Connector which assumes that the application runs in a single instance (rather than distributed nodes)
    using websockets
    """
    host: str = 'localhost'
    port: int = 8000
    received_event_marshaller: MarshallerABC[WebsocketEventABC] = field(default_factory=received_event_marshaller)
    _connections: List[_Connection] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def start(self):
        asyncio.run(self._serve())

    async def _serve(self):
        logger.info('listening:{self.host}:{self.port}')
        async with websockets.serve(self._handle_connection, self.host, self.port):
            await asyncio.Future()  # run forever

    async def _handle_connection(self, websocket):
        connection = _Connection(websocket)
        with self._lock:
            self._connections.append(connection)
        logger.info(f'connected:{connection.id}')
        try:
            async for message in websocket:
                if logger.isEnabledFor(logging.INFO):
                    logger.info(f'received:{connection.id}:{message}')
                event = json.loads(message)
                event_obj = self.received_event_marshaller.load(event)
                event_obj.process(self, str(connection.id))
        finally:
            with self._lock:
                object.__setattr__(self, '_connections', [c for c in self._connections if c.id != connection.id])
            logger.info(f'disconnected:{connection.id}')

    def send(self, channel_key: str, event: ExternalType):
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'channel_send:{channel_key}:{event}')
        for connection in self._connections:
            if channel_key in connection.channel_keys:
                connection.send(event)

    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        connection = next((c for c in self._connections if c.id == connection_id), None)
        if connection:
            return ConnectionInfo(connection.id, frozenset(connection.channel_keys))

    def get_all_connection_info(self, connection_id: str) -> Iterator[ConnectionInfo]:
        for connection in self._connections:
            yield ConnectionInfo(connection.id, frozenset(connection.channel_keys))

    def subscribe(self, connection_id: str, channel_key: str):
        connection = next((c for c in self._connections if c.id == connection_id), None)
        if connection:
            connection.channel_keys.add(channel_key)
            logger.info(f'subscribed:{connection_id}:{channel_key}')

    def unsubscribe(self, connection_id: str, channel_key: str):
        connection = next((c for c in self._connections if c.id == connection_id), None)
        if connection:
            connection.channel_keys.remove(channel_key)
            logger.info(f'unsubscribed:{connection_id}:{channel_key}')
