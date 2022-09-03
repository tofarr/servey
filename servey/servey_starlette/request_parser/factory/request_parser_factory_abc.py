from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Optional

from servey2.action.finder.found_action import FoundAction
from servey2.action.trigger.web_trigger import WebTrigger
from servey2.servey_starlette.request_parser.request_parser_abc import RequestParserABC


class RequestParserFactoryABC(ABC):
    @abstractmethod
    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: Tuple[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        """Render a response"""


def create_parser_factories():
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(RequestParserFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
