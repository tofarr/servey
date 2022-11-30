from dataclasses import dataclass
from typing import Callable, Tuple, Optional

from marshy.types import ExternalItemType
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC
from servey.servey_starlette.response_render.response_render_abc import (
    ResponseRenderABC,
)
from servey.action.trigger.web_trigger import WebTriggerMethod


@dataclass
class ActionEndpoint:
    name: str
    path: str
    fn: Callable
    methods: Tuple[WebTriggerMethod, ...]
    parser: RequestParserABC
    render: ResponseRenderABC
    description: Optional[str] = None

    def to_route(self) -> Route:
        return Route(
            self.path,
            name=self.name,
            endpoint=self.execute,
            methods=[m.value for m in self.methods],
        )

    async def execute(self, request: Request) -> Response:
        kwargs = await self.parser.parse(request)
        result = self.fn(**kwargs)
        response = self.render.render(kwargs, result)
        return response

    def to_openapi_schema(self, schema: ExternalItemType):
        paths: ExternalItemType = schema["paths"]
        components: ExternalItemType = schema["components"]
        path = paths.get(self.path)
        if not path:
            path = paths[self.path] = {}
        for method in self.methods:
            responses = {}
            path_method = path[method.value] = {"responses": responses}
            path_method["operationId"] = self.name
            if self.description:
                path_method["summary"] = self.description
            # Tags?
            self.parser.to_openapi_schema(path_method, components)
            self.render.to_openapi_schema(responses, components)
