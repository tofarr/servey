import json
import os
from dataclasses import dataclass, field
import logging
from threading import Lock
from typing import Iterator, Optional, List, Set
from uuid import uuid4, UUID

from flask import Flask
from flask_sock import Sock
from flask_sock.ws import ConnectionClosed
from marshy import ExternalType, get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from simple_websocket import Server

from servey.connector.connection_info import ConnectionInfo
from servey.connector.connector_abc import ConnectorABC
from servey.connector.connector_meta import ConnectorMeta
from servey.connector.event.websocket_event_abc import WebsocketEventABC
from servey.servey_context import get_default_servey_context
from servey.servey_flask import configure_flask

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _FlaskConnection:
    server: Server
    id: UUID = field(default_factory=uuid4)
    channel_keys: Set[str] = field(default_factory=set)

    def send(self, event: ExternalType):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'connection_send:{self.id}:{event}')
        event_str = json.dumps(event)
        self.server.send(event_str)


def received_event_marshaller():
    return get_default_context().get_marshaller(WebsocketEventABC)


@dataclass(frozen=True)
class FlaskWebsocketConnector(ConnectorABC):
    """ Connector using flask / websockets suitable for a single node"""
    route: str = '/ws'
    received_event_marshaller: MarshallerABC[WebsocketEventABC] = field(default_factory=received_event_marshaller)
    _connections: List[_FlaskConnection] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def wrap(self, flask: Flask):
        sock = Sock(flask)

        @sock.route(self.route)
        def ws(server: Server):
            connection = _FlaskConnection(server)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'Connected:{connection.id}')
            with self._lock:
                self._connections.append(connection)
            try:
                server.send(dict(type='connectionId', id=str(connection.id)))
                while True:
                    message = server.receive(timeout=5)
                    event = json.loads(message)
                    event_obj = self.received_event_marshaller.load(event)
                    event_obj.process(self, str(connection.id))
            except ConnectionClosed as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Disconnected:{connection.id}')
            finally:
                with self._lock:
                    self._connections.remove(connection)

    def get_meta(self) -> ConnectorMeta:
        host = os.environ.get('FLASK_HOST') or 'localhost'
        port = os.environ.get('FLASK_PORT') or '5000'
        url = ConnectorMeta(f'ws://{host}:{port}{self.route}')
        return url

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


if __name__ == '__main__':
    flask_instance = configure_flask()
    connector = FlaskWebsocketConnector()
    connector.wrap(flask_instance)
    servey_context = get_default_servey_context()
    servey_context.connector = connector
    flask_instance.run(
        host=os.environ.get('FLASK_HOST') or '',
        port=int(os.environ.get('FLASK_PORT') or '5000'),
        debug=True
    )
