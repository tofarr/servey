from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

from marshy.types import ExternalItemType
from requests import Response
from starlette.requests import Request
from starlette.routing import Route

from servey.action import Action
from servey.executor import Executor


class ActionRouteABC(ABC):

    @abstractmethod
    def get_action(self) -> Action:
        """ Get the action """

    @abstractmethod
    def get_route(self) -> Route:
        """ Get the route"""

    @abstractmethod
    def get_openapi_schema(self) -> ExternalItemType:
        """ Add this to the openapi schema given """

    async def execute(self, request: Request) -> Response:
        """ Execute the action and return a result """
        executor, kwargs = self.parse(request)
        result = executor.execute(kwargs)
        response = self.render(executor, result)
        return response

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        params = await self.parse_params(request)
        action_meta = self.get_action().action_meta
        action_meta.params_schema.validate(params)
        marshalled = action_meta.params_marshaller.load(params)
        return marshalled

    @abstractmethod
    async def parse_params(self, request: Request) -> ExternalItemType:

    @abstractmethod
    def render(self, executor: Executor, result: Any) -> Response:
        """ Render a result """
