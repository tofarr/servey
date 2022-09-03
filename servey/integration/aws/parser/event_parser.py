from dataclasses import dataclass
from typing import Dict, Any, Tuple

from marshy.types import ExternalItemType

from servey.action import Action
from servey.executor import Executor
from servey.integration.aws.parser.event_parser_abc import EventParserABC


@dataclass
class EventParser(EventParserABC):
    action: Action

    def parse(
        self, event: ExternalItemType, context
    ) -> Tuple[Executor, Dict[str, Any]]:
        executor = self.action.create_executor()
        action_meta = self.action.action_meta
        action_meta.params_schema.validate(event)
        kwargs = action_meta.params_marshaller.load(event)
        return executor, kwargs


class EventParserFactory(EventParserFactoryABC):
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
