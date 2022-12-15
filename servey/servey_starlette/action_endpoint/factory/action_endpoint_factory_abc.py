from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Set

from servey.action.action import Action
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)


class ActionEndpointFactoryABC(ABC):
    priority: 100

    @abstractmethod
    def create(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        """Create an action endpoint"""


def create_endpoint_factories() -> List[ActionEndpointFactoryABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(ActionEndpointFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
