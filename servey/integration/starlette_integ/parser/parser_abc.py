from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Tuple, Optional, List, Any, Dict

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.action import Action
from servey.executor import Executor
from servey.trigger.web_trigger import WebTrigger


class ParserABC(ABC):
    priority: int = 100

    @abstractmethod
    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        """Parse a request"""

    @abstractmethod
    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        """Add an openapi description of this parser to the openapi path/method given"""


class ParserFactoryABC(ABC):
    @abstractmethod
    def create(
        self,
        action: Action,
        trigger: WebTrigger,
        parser_factories: Tuple[ParserFactoryABC],
    ) -> Optional[ParserABC]:
        """Render a response"""


def create_parser_factories():
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(ParserFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
