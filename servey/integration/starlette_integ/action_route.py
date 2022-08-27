from dataclasses import dataclass
from typing import Tuple, Dict, Any

from marshy.types import ExternalItemType
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.schemas import SchemaGenerator

from servey.access_control.allow_all import ALLOW_ALL
from servey.action import Action
from servey.executor import Executor
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

    async def execute(self, request: Request) -> JSONResponse:
        executor, kwargs = self.parse(request)
        result = executor.execute(kwargs)
        action_meta = self.action.action_meta
        dumped = action_meta.result_marshaller.dump(result)
        action_meta.result_schema.validate(dumped)
        return JSONResponse(dumped)

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        action_meta = self.action.action_meta
        params = await request.json()
        action_meta.params_schema.validate(params)
        kwargs = action_meta.params_marshaller.load(params)
        executor = self.action.create_executor()
        return executor, kwargs

    def to_openapi_schema(self, schema: ExternalItemType):
        paths: ExternalItemType = schema["paths"]
        components: ExternalItemType = schema["components"]
        path = paths.get(self.path)
        if not path:
            path = paths[self.path] = {}
        for method in self.methods:
            responses = {}
            path_method = path[method.value()] = {"responses": responses}
            path_method["operationId"] = self.action.action_meta.name
            # Tags?
            self.parser.to_openapi_schema(path_method, components)
            self.render.to_openapi_schema(responses, components)
