import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest import TestCase

from marshy.types import ExternalItemType

from servey.errors import ServeyError
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import ROOT, Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.route_factory import subscription_route_factory

# noinspection PyProtectedMember
from servey.servey_starlette.route_factory.subscription_route_factory import (
    SubscriptionRouteFactory,
    _SubscriptionConnections,
)
from servey.subscription.event_filter_abc import EventFilterABC, T
from servey.subscription.subscription import subscription


class TestSubscriptionRoute(TestCase):
    def test_publish_no_connections(self):
        subscription_ = subscription(str, "messager")
        factory = SubscriptionRouteFactory()
        subscription_service = factory.create([])
        subscription_service.publish(subscription_, "Hello There!")
        # Does nothing

    def test_create(self):
        subscription_ = subscription(str, "foobar")
        subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = {
            "foobar": _SubscriptionConnections(subscription_)
        }
        subscription_route_factory._CONNECTIONS_BY_ID = {}
        try:
            factory = SubscriptionRouteFactory()
            subscription_service = factory.create([subscription_])
            subscription_route = list(factory.create_routes())[0]
            subscription_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            authorizer = get_default_authorizer()
            web_socket.headers["Authorization"] = f"Bearer {authorizer.encode(ROOT)}"
            loop = asyncio.get_event_loop()
            loop.run_until_complete(subscription_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            subscription_service.publish(subscription_, "Hello There!")
            subscription_service.publish(subscription(str, "ping"), "Pong!")
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                subscription_endpoint.on_disconnect(web_socket, 200)
            )
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            self.assertEqual(1, web_socket.accepts)
            self.assertEqual(["Hello There!"], web_socket.sent)
        finally:
            subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = None
            subscription_route_factory._CONNECTIONS_BY_ID = {}

    def test_unauthorized(self):
        subscription_ = subscription(
            str, "foobar", access_control=ScopeAccessControl("root")
        )
        factory = SubscriptionRouteFactory()
        subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = {
            "foobar": _SubscriptionConnections(subscription_)
        }
        subscription_route_factory._CONNECTIONS_BY_ID = {}
        try:
            subscription_route = list(factory.create_routes())[0]
            subscription_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(subscription_endpoint.on_connect(web_socket))
            with self.assertRaises(ServeyError):
                loop.run_until_complete(
                    subscription_endpoint.on_receive(
                        web_socket,
                        json.dumps({"type": "Subscribe", "payload": "foobar"}),
                    )
                )
        finally:
            subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = None
            subscription_route_factory._CONNECTIONS_BY_ID = {}

    def test_unknown_subscription(self):
        try:
            factory = SubscriptionRouteFactory()
            subscription_route = list(factory.create_routes())[0]
            subscription_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(subscription_endpoint.on_connect(web_socket))
            with self.assertRaises(ServeyError):
                loop.run_until_complete(
                    subscription_endpoint.on_receive(
                        web_socket,
                        json.dumps({"type": "Foobar", "payload": "messager"}),
                    )
                )
        finally:
            subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = None
            subscription_route_factory._CONNECTIONS_BY_ID = {}

    def test_filtering(self):
        subscription_ = subscription(str, "foobar", event_filter=NopeEventFilter())
        subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = {
            "foobar": _SubscriptionConnections(subscription_)
        }
        subscription_route_factory._CONNECTIONS_BY_ID = {}
        try:
            factory = SubscriptionRouteFactory()
            subscription_service = factory.create([subscription_])
            subscription_route = list(factory.create_routes())[0]
            subscription_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )
            web_socket = MockWebSocket()
            authorizer = get_default_authorizer()
            web_socket.headers["Authorization"] = f"Bearer {authorizer.encode(ROOT)}"
            loop = asyncio.get_event_loop()
            loop.run_until_complete(subscription_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Unsubscribe", "payload": "foobar"})
                )
            )
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            subscription_service.publish(subscription_, "Hello There!")
            self.assertEqual(1, web_socket.accepts)
            self.assertEqual([], web_socket.sent)
        finally:
            subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = None
            subscription_route_factory._CONNECTIONS_BY_ID = {}

    def test_send_error(self):
        subscription_ = subscription(str, "foobar")
        subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = {
            "foobar": _SubscriptionConnections(subscription_)
        }
        subscription_route_factory._CONNECTIONS_BY_ID = {}
        try:
            factory = SubscriptionRouteFactory()
            subscription_service = factory.create([subscription_])
            subscription_route = list(factory.create_routes())[0]
            subscription_endpoint = subscription_route.endpoint(
                {"type": "websocket"}, None, None
            )

            class ErrorWebSocket(MockWebSocket):
                def send_json(self, event: ExternalItemType):
                    raise ValueError()

            web_socket = ErrorWebSocket()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(subscription_endpoint.on_connect(web_socket))
            loop.run_until_complete(
                subscription_endpoint.on_receive(
                    web_socket, json.dumps({"type": "Subscribe", "payload": "foobar"})
                )
            )
            subscription_service.publish(subscription_, "Hello There!")
        finally:
            subscription_route_factory._SUBSCRIPTION_CONNECTIONS_BY_NAME = None
            subscription_route_factory._CONNECTIONS_BY_ID = {}


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


class NopeEventFilter(EventFilterABC):
    """Filter all events"""

    def should_publish(self, event: T, authorization: Optional[Authorization]) -> bool:
        return False
