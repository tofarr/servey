from dataclasses import dataclass
from typing import Tuple

from marshy.types import ExternalItemType
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from servey.action import Action
from servey.integration.starlette_integ.parser.parser_abc import ParserABC
from servey.integration.starlette_integ.render.render_abc import RenderABC
from servey.trigger.web_trigger import WebTriggerMethod


@dataclass(frozen=True)
class ActionRoute:
    path: str
    methods: Tuple[WebTriggerMethod, ...]
    action: Action
    parser: ParserABC
    render: RenderABC

    def to_route(self) -> Route:
        return Route(
            self.path, endpoint=self.execute, methods=[m.value for m in self.methods]
        )

    async def execute(self, request: Request) -> Response:
        executor, kwargs = await self.parser.parse(request)
        result = executor.execute(**kwargs)
        return self.render.render(executor, result)

    def to_openapi_schema(self, schema: ExternalItemType):
        paths: ExternalItemType = schema["paths"]
        components: ExternalItemType = schema["components"]
        path = paths.get(self.path)
        if not path:
            path = paths[self.path] = {}
        for method in self.methods:
            responses = {}
            path_method = path[method.value] = {"responses": responses}
            path_method["operationId"] = self.action.action_meta.name
            if self.action.action_meta.description:
                path_method["summary"] = self.action.action_meta.description
            # Tags?
            self.parser.to_openapi_schema(path_method, components)
            self.render.to_openapi_schema(responses, components)
