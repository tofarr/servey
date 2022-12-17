from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict, Any
from urllib.request import Request

from marshy.types import ExternalItemType
from requests import Response
from starlette.routing import Route

from servey.action.action import Action


class ActionEndpointABC(ABC):
    @abstractmethod
    def get_action(self) -> Action:
        """Get the action for this endpoint"""

    @abstractmethod
    def get_route(self) -> Route:
        """
        Convert this endpoint to a route which may be used by starlette
        """

    @abstractmethod
    async def execute_with_context(
        self, request: Request, context: Dict[str, Any]
    ) -> Response:
        """
        Execute the action for this endpoint with the request and overrides given
        """

    async def execute(self, request: Request) -> Response:
        response = await self.execute_with_context(request, {})
        return response

    @abstractmethod
    def to_openapi_schema(self, schema: ExternalItemType):
        """
        Merge the openapi schema for this endpoint into the schema given
        """
