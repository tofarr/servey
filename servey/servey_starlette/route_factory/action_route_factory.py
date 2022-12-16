from dataclasses import dataclass, field
from typing import Iterator, List

from starlette.routing import Route

from servey.action.action import Action
from servey.finder.action_finder_abc import find_actions
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)

from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    create_endpoint_factories,
)
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC


@dataclass
class ActionRouteFactory(RouteFactoryABC):
    """Utility for mounting actions to fastapi_integration."""

    action_endpoint_factories: List[ActionEndpointFactory] = field(
        default_factory=create_endpoint_factories
    )

    def create_routes(self) -> Iterator[Route]:
        for action in find_actions():
            route = self.create_route(action)
            if route:
                yield route

    def create_route(self, action: Action) -> Route:
        action_endpoint = self.create_action_endpoint(action)
        if action_endpoint:
            route = action_endpoint.get_route()
            return route

    def create_action_endpoint(self, action: Action) -> ActionEndpointABC:
        for factory in self.action_endpoint_factories:
            action_endpoint = factory.create(
                action, set(), self.action_endpoint_factories
            )
            if action_endpoint:
                return action_endpoint
