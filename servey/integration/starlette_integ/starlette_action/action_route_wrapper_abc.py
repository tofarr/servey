from abc import ABC
from dataclasses import dataclass
from typing import Any, Tuple, Dict

from marshy.types import ExternalItemType
from requests import Response
from starlette.requests import Request
from starlette.routing import Route

from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.starlette_action.action_route_abc import (
    ActionRouteABC,
)


@dataclass
class ActionRouteWrapperABC(ActionRouteABC, ABC):
    action_route: ActionRouteABC

    def get_action(self) -> Action:
        return self.action_route.get_action()

    def get_route(self) -> Route:
        return self.action_route.get_route()

    def get_openapi_schema(self) -> ExternalItemType:
        return self.action_route.get_openapi_schema()

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        return await self.action_route.parse(request)

    def render(self, executor: Executor, result: Any) -> Response:
        return self.action_route.render(executor, result)
