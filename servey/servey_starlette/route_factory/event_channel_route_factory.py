import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Iterator, Optional, Dict, List, Set
from uuid import uuid4

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

from servey.errors import ServeyError
from servey.event_channel.websocket.event_filter_abc import EventFilterABC

from servey.event_channel.websocket.websocket_channel import WebsocketChannel
from servey.event_channel.websocket.websocket_sender import (
    WebsocketSenderFactoryABC,
    WebsocketSenderABC,
    T,
)
from servey.finder.event_channel_finder_abc import find_channels_by_type
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

LOGGER = logging.getLogger(__name__)


@dataclass
class EventChannelRouteFactory(RouteFactoryABC, WebsocketSenderFactoryABC):
    path: str = "/subscription"

    def create_routes(self) -> Iterator[Route]:
        should_create_route = next(
            (True for _ in find_channels_by_type(WebsocketChannel)), False
        )
        if should_create_route:
            route = WebSocketRoute(self.path, _WebsocketChannelEndpoint)
            yield route

    def create(
        self,
        channel_name: str,
        event_schema: Schema,
        access_control: AccessControlABC = ALLOW_ALL,
        event_filter: Optional[EventFilterABC] = None,
    ) -> Optional[WebsocketSenderABC]:
        event_marshaller = get_default_context().get_marshaller(
            event_schema.python_type
        )
        return _StarletteSender(event_marshaller, event_filter)


class _WebsocketChannelEndpoint(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        authorization = None
        token = websocket.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
            authorizer = get_default_authorizer()
            authorization = authorizer.authorize(token)

        connection = _Connection(
            connection_id=str(uuid4()), websocket=websocket, authorization=authorization
        )
        # noinspection PyArgumentList
        LOGGER.debug("connect:{connection_id}", connection_id=connection.connection_id)
        websocket.path_params["connection_id"] = connection.connection_id
        _get_connections_by_id()[connection.connection_id] = connection

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        connection_id = websocket.path_params["connection_id"]
        # noinspection PyArgumentList
        LOGGER.debug("disconnect:{connection_id}", connection_id=connection_id)
        connections_by_id = _get_connections_by_id()
        connection = connections_by_id.pop(connection_id)
        subscription_connections_by_name = _get_connections_by_name()
        for channel_name in connection.channel_names:
            subscription_connections_by_name[channel_name].connections.remove(
                connection
            )

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        event = json.loads(data)
        type_ = event["type"]
        connection_id = websocket.path_params["connection_id"]
        connection = _get_connections_by_id().get(connection_id)
        if not connection:
            LOGGER.warning(f"unknown_connection:{connection_id}")
            return
        if type_ == "Subscribe":
            channel_name = event["payload"]
            if channel_name in connection.channel_names:
                return
            channel_connection = _get_connections_by_name()[channel_name]
            if not channel_connection.channel.access_control.is_executable(
                connection.authorization
            ):
                raise ServeyError("unauthorized")
            channel_connection.connections.append(connection)
            connection.channel_names.add(channel_name)
        elif type_ == "Unsubscribe":
            channel_name = event["payload"]
            if channel_name not in connection.channel_names:
                return
            subscription_connection = _get_connections_by_name()[channel_name]
            subscription_connection.connections.remove(connection)
            connection.channel_names.remove(channel_name)
        else:
            raise ServeyError(f"unknown_type:{type_}")


@dataclass
class _Connection:
    connection_id: str
    websocket: WebSocket
    channel_names: Set[str] = field(default_factory=set)
    authorization: Optional[Authorization] = None


@dataclass
class _ChannelConnections:
    channel: WebsocketChannel
    connections: List[_Connection] = field(default_factory=list)


_CONNECTIONS_BY_NAME: Optional[Dict[str, _ChannelConnections]] = None
_CONNECTIONS_BY_ID: Dict[str, _Connection] = {}


# pylint: disable=W0603
def _get_connections_by_name() -> Dict[str, _ChannelConnections]:
    global _CONNECTIONS_BY_NAME
    if _CONNECTIONS_BY_NAME is None:
        _CONNECTIONS_BY_NAME = {
            channel.name: _ChannelConnections(channel)
            for channel in find_channels_by_type(WebsocketChannel)
        }
    return _CONNECTIONS_BY_NAME


def _get_connections_by_id() -> Dict[str, _Connection]:
    return _CONNECTIONS_BY_ID


@dataclass
class _StarletteSender(WebsocketSenderABC):
    event_marshaller: MarshallerABC[T]
    event_filter: Optional[EventFilterABC[T]]

    def send(self, channel_name: str, event: T):
        connections = _get_connections_by_name().get(channel_name)
        if not connections:
            return
        loop = asyncio.get_event_loop()
        json_event = self.event_marshaller.dump(event)
        for connection in connections.connections:
            # noinspection PyBroadException
            try:
                if self.event_filter and not self.event_filter.should_publish(
                    event, connection.authorization
                ):
                    continue
                sending = connection.websocket.send_json(json_event)
                loop.create_task(sending)
            except Exception:
                LOGGER.exception("failed_to_send_data")
