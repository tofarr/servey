import os
from dataclasses import field
from typing import Iterator

from schemey.util import filter_none
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.action_context import get_default_action_context
from servey.integration.starlette_integ.route_factory.action_route_factory import (
    ActionRouteFactory,
)
from servey.integration.starlette_integ.route_factory.route_factory_abc import (
    RouteFactoryABC,
)


class OpenapiRouteFactory(RouteFactoryABC):
    title: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_TITLE" or "Servey")
    )
    description: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_DESCRIPTION")
    )
    version: str = field(
        default_factory=lambda: os.environ.get("SERVEY_API_VERSION" or "0.1.0")
    )
    action_route_factory: ActionRouteFactory = field(default_factory=ActionRouteFactory)

    def create_routes(self) -> Iterator[Route]:
        yield Route(
            "/openapi.json", endpoint=self.openapi_schema, include_in_schema=False
        )
        yield Route("/docs", endpoint=self.docs, include_in_schema=False)

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
        action_context = get_default_action_context()
        for action_route in self.action_route_factory.create_action_routes(
            action_context
        ):
            action_route.to_openapi_schema(schema)
        return JSONResponse(schema)

    def docs(self, request: Request) -> Response:
        # TODO: Dump swagger docs here...
        return JSONResponse(True)
