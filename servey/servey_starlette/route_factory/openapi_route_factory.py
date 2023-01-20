import os
from dataclasses import field, dataclass
from typing import Iterator

from marshy.types import ExternalItemType
from schemey.util import filter_none
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from servey.finder.action_finder_abc import find_actions
from servey.servey_starlette.route_factory.action_route_factory import (
    ActionRouteFactory,
)
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC


@dataclass
class OpenapiRouteFactory(RouteFactoryABC):
    title: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_TITLE") or "Servey"
    )
    description: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_DESCRIPTION")
    )
    version: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_VERSION") or "0.1.0"
    )
    action_route_factory: ActionRouteFactory = field(default_factory=ActionRouteFactory)
    debug: bool = field(
        default_factory=lambda: int(os.environ.get("SERVER_DEBUG", "1")) == 1
    )

    def create_routes(self) -> Iterator[Route]:
        if not self.debug:
            return
        # add as template route
        yield Route("/openapi.json", endpoint=self.endpoint, include_in_schema=False)
        yield Mount(
            "/docs",
            app=StaticFiles(packages=["servey.servey_starlette"], html=True),
            name="docs",
        )

    # noinspection PyUnusedLocal
    def endpoint(self, request: Request) -> Response:
        schema = self.openapi_schema()
        return JSONResponse(schema)

    def openapi_schema(self) -> ExternalItemType:
        schema = {
            "openapi": "3.0.2",
            "info": filter_none(
                {
                    "title": self.title,
                    "version": self.version,
                    "description": self.description,
                }
            ),
            "paths": {},
            "components": {},
        }
        if os.environ.get("SERVER_HOST"):
            schema["servers"] = [{"url": os.environ.get("SERVER_HOST")}]
        for action in find_actions():
            action_endpoint = self.action_route_factory.create_action_endpoint(action)
            if action_endpoint:
                action_endpoint.to_openapi_schema(schema)
        return schema
