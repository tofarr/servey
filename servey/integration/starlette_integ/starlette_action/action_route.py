from dataclasses import dataclass
from typing import Tuple, Dict, Any

from marshy.types import ExternalItemType
from requests import Response
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.starlette_action.action_route_abc import (
    ActionRouteABC,
)
from servey.trigger.web_trigger import WebTriggerMethod


@dataclass
class ActionRoute(ActionRouteABC, ABC):
    action: Action
    path: str
    method: WebTriggerMethod

    def get_action(self) -> Action:
        return self.action

    def get_route(self) -> Route:
        return Route(self.path, endpoint=self.execute, methods=[self.method.value])

    async def execute(self, request: Request) -> Response:
        executor, kwargs = self.parse(request)
        result = executor.execute(kwargs)
        response = self.render(executor, result)

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        action_meta = self.action.action_meta
        params = await request.json()
        action_meta.params_schema.validate(params)
        kwargs = action_meta.params_marshaller.load(params)
        executor = self.action.create_executor()
        return executor, kwargs

    def render(self, executor: Executor, result: Any) -> Response:
        action_meta = self.action.action_meta
        dumped = action_meta.result_marshaller.dump(result)
        action_meta.result_schema.validate(dumped)
        return JSONResponse(dumped)

    def move_refs_to_component_schemas(
        self, schema: ExternalItemType, openapi_schema: ExternalItemType
    ) -> ExternalItemType:
        pass
