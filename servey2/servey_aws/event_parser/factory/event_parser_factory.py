from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext

from servey2.action.finder.found_action import FoundAction
from servey2.servey_aws.event_parser.event_parser import EventParser
from servey2.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey2.servey_aws.event_parser.factory.event_parser_factory_abc import EventParserFactoryABC
from servey2.servey_starlette.request_parser.factory.body_parser_factory import get_marshaller_for_params


@dataclass
class EventParserFactory(EventParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    priority: int = 50

    def create(self, action: FoundAction, factories: Tuple[EventParserFactoryABC, ...]) -> Optional[EventParserABC]:
        marshaller = get_marshaller_for_params(action.fn, self.marshaller_context)
        return EventParser(marshaller)
