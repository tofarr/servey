import os
from dataclasses import field, dataclass
from typing import Iterator, List, Union

from marshy.types import ExternalItemType
from schemey import Schema
from schemey.util import filter_none
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.action.util import move_ref_items_to_components
from servey.event_channel.websocket.websocket_event_channel import WebsocketEventChannel
from servey.finder.event_channel_finder_abc import find_event_channels_by_type
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC


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
    def get_websocket_channels() -> List[WebsocketEventChannel]:
        result = list(find_event_channels_by_type(WebsocketEventChannel))
        return result

    def create_routes(self) -> Iterator[Route]:
        if self.get_websocket_channels():
            yield Route(
                "/asyncapi.json", endpoint=self.endpoint, include_in_schema=False
            )
        # There is no "async-docs" endpoint - maybe there should be?

    # pylint: disable=W0613
    # noinspection PyUnusedLocal
    def endpoint(self, request: Request) -> Response:
        schema = self.asyncapi_schema()
        return JSONResponse(schema)

    def asyncapi_schema(self) -> ExternalItemType:
        components = {}
        payload_schema = channel_event_schema(self.get_websocket_channels(), components)
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


def channel_event_schema(
    channels: List[WebsocketEventChannel], components: ExternalItemType
) -> Schema:
    any_of = []
    for channel in channels:
        schema = channel.event_schema.schema
        schema = move_ref_items_to_components(schema, schema, components)
        any_of.append(
            {
                "properties": {"type": {"const": type.__name__}, "payload": schema},
                "additionalProperties": False,
                "required": ["type", "payload"],
            }
        )
    type_ = Union[tuple(c.event_schema.python_type for c in channels)]
    return Schema({"anyOf": any_of}, type_)
