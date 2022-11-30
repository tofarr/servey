from abc import ABC, abstractmethod
from typing import Optional, List

from servey.action.finder.found_action import FoundAction
from servey.servey_starlette.response_render.response_render_abc import (
    ResponseRenderABC,
)


class ResponseRenderFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(self, action: FoundAction) -> Optional[ResponseRenderABC]:
        """Render a response"""


def create_render_factories() -> List[ResponseRenderFactoryABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(ResponseRenderFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
