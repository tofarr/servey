import os
from dataclasses import field, dataclass
from typing import Iterator, List

from marshy.types import ExternalItemType
from schemey.util import filter_none
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.finder.subscription_finder_abc import find_subscriptions
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC
from servey.subscription.subscription import Subscription
from servey.subscription.subscription_event import subscription_event_schema


@dataclass
class AsyncapiRouteFactory(RouteFactoryABC):
    title: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_TITLE") or "Servey"
    )
    description: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_DESCRIPTION")
    )
    version: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_VERSION") or "0.1.0"
    )

    @staticmethod
    def get_subscribable() -> List[Subscription]:
        result = [s for s in find_subscriptions() if s.access_control != ALLOW_NONE]
        return result

    def create_routes(self) -> Iterator[Route]:
        if self.get_subscribable():
            yield Route(
                "/asyncapi.json", endpoint=self.endpoint, include_in_schema=False
            )
        # There is no "async-docs" endpoint - maybe there should be?

    # noinspection PyUnusedLocal
    def endpoint(self, request: Request) -> Response:
        schema = self.asyncapi_schema()
        return JSONResponse(schema)

    def asyncapi_schema(self) -> ExternalItemType:
        components = {}
        payload_schema = subscription_event_schema(self.get_subscribable(), components)
        schema = {
            "asyncapi": "2.5.0",
            "info": filter_none(
                {
                    "title": self.title,
                    "version": self.version,
                    "description": self.description,
                }
            ),
            "channels": {
                "/subscription": {
                    "publish": {
                        "message": {
                            "payload": {
                                "properties": {
                                    "type": {"enum": ["Subscribe", "Unsubscribe"]},
                                    "payload": {"type": "string"},
                                },
                                "additionalProperties": False,
                            }
                        }
                    },
                    "subscribe": {"message": {"payload": payload_schema.schema}},
                }
            },
            "components": components,
        }
        server_ws_url = os.environ.get("SERVER_WS_URL")
        if server_ws_url:
            schema["servers"] = {
                "production": {"url": server_ws_url, "protocol": "wss"}
            }
        return schema
