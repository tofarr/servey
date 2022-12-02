from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Callable

from marshy.types import ExternalItemType

from servey.action.finder.found_action import FoundAction
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


class ResultRenderFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(
        self, fn: Callable, event: ExternalItemType, context, parser: EventParserABC
    ) -> Optional[ResultRenderABC]:
        """Create an event parser"""


def create_render_factories() -> Tuple[ResultRenderFactoryABC, ...]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(ResultRenderFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return tuple(factories)
