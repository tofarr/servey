from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

from marshy.types import ExternalItemType

from servey.executor import Executor


class EventParserABC(ABC):
    @abstractmethod
    def parse(
        self, event: ExternalItemType, context
    ) -> Tuple[Executor, Dict[str, Any]]:
        """Parse a request"""


class EventParserFactoryABC(ABC):
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
