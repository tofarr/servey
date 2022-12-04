from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType

from servey.action.action import get_marshaller_for_params
from servey.servey_aws.event_parser.api_gateway_event_parser import (
    ApiGatewayEventParser,
)
from servey.servey_aws.event_parser.appsync_event_parser import AppsyncEventParser
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    EventParserFactoryABC,
)


@dataclass
class AppsyncEventParserFactory(EventParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    priority: int = 100

    def create(
        self, fn: Callable, event: ExternalItemType, context
    ) -> Optional[EventParserABC]:
        info = event.get("info") or {}
        variables = info.get("variables")
        if variables is None:
            return
        marshaller = get_marshaller_for_params(fn, self.marshaller_context)
        return AppsyncEventParser(marshaller)
