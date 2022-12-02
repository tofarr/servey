from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Callable

from marshy.types import ExternalItemType

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


class EventParserFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(
        self, fn: Callable, event: ExternalItemType, context
    ) -> Optional[EventParserABC]:
        """Create an event parser"""


def create_parser_factories() -> Tuple[EventParserFactoryABC, ...]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(EventParserFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return tuple(factories)
