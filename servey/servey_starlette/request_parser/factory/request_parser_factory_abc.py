from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List

from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC


class RequestParserFactoryABC(ABC):
    @abstractmethod
    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: List[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        """Render a response"""


def create_parser_factories() -> List[RequestParserFactoryABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    factories = [f() for f in get_impls(RequestParserFactoryABC)]
    factories.sort(key=lambda f: f.priority, reverse=True)
    return factories
