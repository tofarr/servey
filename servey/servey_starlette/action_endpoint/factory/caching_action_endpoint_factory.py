from dataclasses import dataclass
from typing import List, Optional, Set

from servey.action.action import Action
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.action_endpoint.caching_action_endpoint import (
    CachingActionEndpoint,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    ActionEndpointFactoryABC,
)


@dataclass
class CachingActionEndpointFactory(ActionEndpointFactoryABC):
    priority: int = 150
    skip: bool = False

    def create(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        if self.skip or not action.cache_control:
            return
        action_endpoint = self._get_wrapped_endpoint(action, skip_args, factories)
        if action_endpoint:
            return CachingActionEndpoint(action_endpoint)

    def _get_wrapped_endpoint(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        self.skip = True
        try:
            for factory in factories:
                action_endpoint = factory.create(action, skip_args, factories)
                if action_endpoint:
                    return action_endpoint
        finally:
            self.skip = False
