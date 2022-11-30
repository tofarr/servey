from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional

from schemey import get_default_schema_context, SchemaContext

from servey.action.action import get_schema_for_params
from servey.action.finder.found_action import FoundAction
from servey.servey_aws.event_parser.event_parser import EventParser
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    EventParserFactoryABC,
)
from servey.servey_aws.event_parser.validating_event_parser import ValidatingEventParser


@dataclass
class ValidatingEventParserFactory(EventParserFactoryABC):
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    priority: int = 50
    skip: bool = False

    def create(
        self, action: FoundAction, factories: Tuple[EventParserFactoryABC, ...]
    ) -> Optional[EventParserABC]:
        if self.skip:
            return
        schema = get_schema_for_params(action.fn, self.schema_context)
        self.skip = True
        try:
            for factory in factories:
                parser = factory.create(action, factories)
                if parser:
                    return ValidatingEventParser(parser, schema)
        finally:
            self.skip = False
