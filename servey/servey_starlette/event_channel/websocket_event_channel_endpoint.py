import json
import logging
from uuid import uuid4

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from servey.errors import ServeyError
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.event_channel.local import (
    LocalConnection,
    get_connections_by_id,
    get_connections_by_name,
)

LOGGER = logging.getLogger(__name__)


class WebsocketEventChannelEndpoint(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        authorization = None
        token = websocket.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
            authorizer = get_default_authorizer()
            authorization = authorizer.authorize(token)

        connection = LocalConnection(
            connection_id=str(uuid4()), websocket=websocket, authorization=authorization
        )
        # noinspection PyArgumentList
        LOGGER.debug("connect:{connection_id}", connection_id=connection.connection_id)
        websocket.path_params["connection_id"] = connection.connection_id
        get_connections_by_id()[connection.connection_id] = connection

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        connection_id = websocket.path_params["connection_id"]
        # noinspection PyArgumentList
        LOGGER.debug("disconnect:{connection_id}", connection_id=connection_id)
        connections_by_id = get_connections_by_id()
        connection = connections_by_id.pop(connection_id)
        subscription_connections_by_name = get_connections_by_name()
        for channel_name in connection.channel_names:
            subscription_connections_by_name[channel_name].connections.remove(
                connection
            )

    async def on_receive(self, websocket: WebSocket, data: str) -> None:
        event = json.loads(data)
        type_ = event["type"]
        connection_id = websocket.path_params["connection_id"]
        connection = get_connections_by_id().get(connection_id)
        if not connection:
            LOGGER.warning(f"unknown_connection:{connection_id}")
            return
        if type_ == "Subscribe":
            channel_name = event["payload"]
            if channel_name in connection.channel_names:
                return
            channel_connection = get_connections_by_name()[channel_name]
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
            subscription_connection = get_connections_by_name()[channel_name]
            subscription_connection.connections.remove(connection)
            connection.channel_names.remove(channel_name)
        else:
            raise ServeyError(f"unknown_type:{type_}")
