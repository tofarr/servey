import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest import TestCase

from marshy.types import ExternalItemType
from schemey.schema import str_schema

from servey.errors import ServeyError
from servey.event_channel.websocket.event_filter_abc import EventFilterABC, T
from servey.event_channel.websocket.websocket_event_channel import (
    websocket_event_channel,
)
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import ROOT, Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.event_channel import local
from servey.servey_starlette.event_channel.local import LocalChannelConnections
from servey.servey_starlette.event_channel.starlette_websocket_sender_factory import (
    StarletteWebsocketSenderFactory,
)
from servey.servey_starlette.route_factory.event_channel_route_factory import (
    EventChannelRouteFactory,
)


class TestEventChannelRoute(TestCase):
    def test_publish_no_connections(self):
        channel = websocket_event_channel("messager", str)
        channel.publish("Hello There!")
        # Does nothing

    def test_create(self):
        channel = websocket_event_channel("foobar", str)
        local.CONNECTIONS_BY_NAME = {"foobar": LocalChannelConnections(channel)}
        local.CONNECTIONS_BY_ID = {}
        try:
            route_factory = EventChannelRouteFactory()
            sender_factory = StarletteWebsocketSenderFactory()
            sender = sender_factory.create("foobar", str_schema())
            sender_route = list(route_factory.create_routes())[0]
            event_channel_endpoint = sender_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            authorizer = get_default_authorizer()
            web_socket.headers["Authorization"] = f"Bearer {authorizer.encode(ROOT)}"
            loop = asyncio.get_event_loop()
            loop.run_until_complete(event_channel_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            sender.send("foobar", "Hello There!")
            sender.send("ping", "Pong!")
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                event_channel_endpoint.on_disconnect(web_socket, 200)
            )
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            self.assertEqual(1, web_socket.accepts)
            self.assertEqual(["Hello There!"], web_socket.sent)
        finally:
            local.CONNECTIONS_BY_NAME = None
            local.CONNECTIONS_BY_ID = {}

    def test_unauthorized(self):
        channel = websocket_event_channel(
            "foobar", str, access_control=ScopeAccessControl("root")
        )
        factory = EventChannelRouteFactory()
        local.CONNECTIONS_BY_NAME = {"foobar": LocalChannelConnections(channel)}
        local.CONNECTIONS_BY_ID = {}
        try:
            subscription_route = list(factory.create_routes())[0]
            event_channel_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(event_channel_endpoint.on_connect(web_socket))
            with self.assertRaises(ServeyError):
                loop.run_until_complete(
                    event_channel_endpoint.on_receive(
                        web_socket,
                        json.dumps({"type": "Subscribe", "payload": "foobar"}),
                    )
                )
        finally:
            local.CONNECTIONS_BY_NAME = None
            local.CONNECTIONS_BY_ID = {}

    def test_unknown_subscription(self):
        try:
            factory = EventChannelRouteFactory()
            subscription_route = list(factory.create_routes())[0]
            event_channel_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(event_channel_endpoint.on_connect(web_socket))
            with self.assertRaises(ServeyError):
                loop.run_until_complete(
                    event_channel_endpoint.on_receive(
                        web_socket,
                        json.dumps({"type": "Foobar", "payload": "messager"}),
                    )
                )
        finally:
            local.CONNECTIONS_BY_NAME = None
            local.CONNECTIONS_BY_ID = {}

    def test_filtering(self):
        channel = websocket_event_channel("foobar", str, event_filter=NopeEventFilter())
        local.CONNECTIONS_BY_NAME = {"foobar": LocalChannelConnections(channel)}
        local.CONNECTIONS_BY_ID = {}
        try:
            route_factory = EventChannelRouteFactory()
            sender_factory = StarletteWebsocketSenderFactory()
            sender = sender_factory.create("foobar", str_schema())
            channel_route = list(route_factory.create_routes())[0]
            event_channel_endpoint = channel_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            authorizer = get_default_authorizer()
            web_socket.headers["Authorization"] = f"Bearer {authorizer.encode(ROOT)}"
            loop = asyncio.get_event_loop()
            loop.run_until_complete(event_channel_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            sender.send("foobar", "Hello There!")
            self.assertEqual(1, web_socket.accepts)
            self.assertEqual([], web_socket.sent)
        finally:
            local.CONNECTIONS_BY_NAME = None
            local.CONNECTIONS_BY_ID = {}

    def test_send_error(self):
        channel = websocket_event_channel("foobar", str)
        local.CONNECTIONS_BY_NAME = {"foobar": LocalChannelConnections(channel)}
        local.CONNECTIONS_BY_ID = {}
        try:
            route_factory = EventChannelRouteFactory()
            sender_factory = StarletteWebsocketSenderFactory()
            sender = sender_factory.create("foobar", str_schema())
            subscription_route = list(route_factory.create_routes())[0]
            event_channel_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )

            class ErrorWebSocket(MockWebSocket):
                def send_json(self, event: ExternalItemType):
                    raise ValueError()

            web_socket = ErrorWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(event_channel_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                event_channel_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            sender.send("foobar", "Hello There!")
        finally:
            local.CONNECTIONS_BY_NAME = None
            local.CONNECTIONS_BY_ID = {}


@dataclass
class MockWebSocket:
    headers: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    accepts: int = 0
    sent: List[ExternalItemType] = field(default_factory=list)

    async def accept(self):
        self.accepts += 1

    async def send_json(self, event: ExternalItemType):
        self.sent.append(event)


class NopeEventFilter(EventFilterABC[T]):
    """Filter all events"""

    def should_publish(self, event: T, authorization: Optional[Authorization]) -> bool:
        return False
