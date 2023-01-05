import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Iterator, Optional, Dict, List, Set
from uuid import uuid4

from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

from servey.errors import ServeyError
from servey.finder.subscription_finder_abc import find_subscriptions
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC
from servey.subscription.subscription import Subscription, T
from servey.subscription.subscription_service import (
    SubscriptionServiceFactoryABC,
    SubscriptionServiceABC,
)

LOGGER = logging.getLogger(__name__)


@dataclass
class SubscriptionRouteFactory(RouteFactoryABC, SubscriptionServiceFactoryABC):
    path: str = "/subscription"

    def create_routes(self) -> Iterator[Route]:
        if _get_subscription_connections_by_name():
            route = WebSocketRoute(self.path, _SubscriptionEndpoint)
            yield route

    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        if _get_subscription_connections_by_name():
            return _StarletteSubscriptionService()


class _SubscriptionEndpoint(WebSocketEndpoint):
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
        LOGGER.debug("connect:{connection_id}", connection_id=connection.connection_id)
        websocket.path_params["connection_id"] = connection.connection_id
        _get_connections_by_id()[connection.connection_id] = connection

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        connection_id = websocket.path_params["connection_id"]
        LOGGER.debug("disconnect:{connection_id}", connection_id=connection_id)
        connections_by_id = _get_connections_by_id()
        connection = connections_by_id.pop(connection_id)
        subscription_connections_by_name = _get_subscription_connections_by_name()
        for subscription_name in connection.subscription_names:
            subscription_connections_by_name[subscription_name].connections.remove(
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
            subscription_name = event["payload"]
            if subscription_name in connection.subscription_names:
                return
            subscription_connection = _get_subscription_connections_by_name()[
                subscription_name
            ]
            if not subscription_connection.subscription.access_control.is_executable(
                connection.authorization
            ):
                raise ServeyError("unauthorized")
            subscription_connection.connections.append(connection)
            connection.subscription_names.add(subscription_name)
        elif type_ == "Unsubscribe":
            subscription_name = event["payload"]
            if subscription_name not in connection.subscription_names:
                return
            subscription_connection = _get_subscription_connections_by_name()[
                subscription_name
            ]
            subscription_connection.connections.remove(connection)
            connection.subscription_names.remove(subscription_name)
        else:
            raise ServeyError(f"unknown_type:{type_}")


@dataclass
class _Connection:
    connection_id: str
    websocket: WebSocket
    subscription_names: Set[str] = field(default_factory=set)
    authorization: Optional[Authorization] = None


@dataclass
class _SubscriptionConnections:
    subscription: Subscription
    connections: List[_Connection] = field(default_factory=list)


_SUBSCRIPTION_CONNECTIONS_BY_NAME: Optional[Dict[str, _SubscriptionConnections]] = None
_CONNECTIONS_BY_ID: Dict[str, _Connection] = {}


def _get_subscription_connections_by_name() -> Dict[str, _SubscriptionConnections]:
    global _SUBSCRIPTION_CONNECTIONS_BY_NAME
    if _SUBSCRIPTION_CONNECTIONS_BY_NAME is None:
        _SUBSCRIPTION_CONNECTIONS_BY_NAME = {
            s.name: _SubscriptionConnections(s)
            for s in find_subscriptions()
            if s.access_control != ALLOW_NONE
        }
    return _SUBSCRIPTION_CONNECTIONS_BY_NAME


def _get_connections_by_id() -> Dict[str, _Connection]:
    return _CONNECTIONS_BY_ID


class _StarletteSubscriptionService(SubscriptionServiceABC):
    def publish(self, subscription: Subscription[T], event: T):
        subscription_connections = _get_subscription_connections_by_name().get(
            subscription.name
        )
        if not subscription_connections:
            return
        loop = asyncio.get_event_loop()
        json_event = subscription.event_marshaller.dump(event)
        for connection in subscription_connections.connections:
            # noinspection PyBroadException
            try:
                if (
                    subscription.event_filter
                    and not subscription.event_filter.should_publish(
                        event, connection.authorization
                    )
                ):
                    continue
                sending = connection.websocket.send_json(json_event)
                loop.create_task(sending)
            except Exception:
                LOGGER.exception("failed_to_send_data")
