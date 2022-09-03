from abc import ABC, abstractmethod
from typing import Optional, List

from servey.integration.starlette_integ.render.render_abc import RenderFactoryABC
from servey2.action.finder.found_action import FoundAction
from servey2.servey_starlette.response_render.response_render_abc import ResponseRenderABC


class ResponseRenderFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(self, action: FoundAction) -> Optional[ResponseRenderABC]:
        """Render a response"""


def create_render_factories() -> List[RenderFactoryABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(RenderFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
