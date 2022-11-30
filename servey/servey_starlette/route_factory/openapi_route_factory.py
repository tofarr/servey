import os
from dataclasses import field, dataclass
from typing import Iterator

from schemey.util import filter_none
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.trigger.web_trigger import WebTrigger
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

    def create_routes(self) -> Iterator[Route]:
        yield Route(
            "/openapi.json", endpoint=self.openapi_schema, include_in_schema=False
        )
        yield Mount(
            "/docs",
            app=StaticFiles(packages=["servey.servey_starlette"], html=True),
            name="docs",
        )

    def openapi_schema(self, request: Request) -> Response:
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
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            action_endpoint = self.action_route_factory.create_action_endpoint(
                action, trigger
            )
            action_endpoint.to_openapi_schema(schema)
        return JSONResponse(schema)
