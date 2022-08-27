from abc import abstractmethod, ABC
from typing import Any, Optional, List

from marshy.types import ExternalItemType
from requests import Response

from servey.action import Action
from servey.executor import Executor


class RenderABC(ABC):
    @abstractmethod
    def render(self, executor: Executor, result: Any) -> Response:
        """Render a response"""

    @abstractmethod
    def to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        """Add an openapi description of this render to the openapi path/method/responses given"""


class RenderFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(self, action: Action) -> Optional[RenderABC]:
        """Render a response"""


def create_render_factories() -> List[RenderFactoryABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(RenderFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
