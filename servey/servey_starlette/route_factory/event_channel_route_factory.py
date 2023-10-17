import logging
from dataclasses import dataclass
from typing import Iterator

from starlette.routing import Route, WebSocketRoute

from servey.event_channel.websocket.websocket_event_channel import WebsocketEventChannel
from servey.finder.event_channel_finder_abc import find_event_channels_by_type
from servey.servey_starlette.event_channel.websocket_event_channel_endpoint import (
    WebsocketEventChannelEndpoint,
)
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

LOGGER = logging.getLogger(__name__)


@dataclass
class EventChannelRouteFactory(RouteFactoryABC):
    path: str = "/subscription"

    def create_routes(self) -> Iterator[Route]:
        should_create_route = next(
            (True for _ in find_event_channels_by_type(WebsocketEventChannel)), False
        )
        if should_create_route:
            route = WebSocketRoute(self.path, WebsocketEventChannelEndpoint)
            yield route
