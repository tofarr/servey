from dataclasses import dataclass
from typing import Dict, Any

from marshy.types import ExternalItemType
from schemey import Schema

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class ValidatingEventParser(EventParserABC):
    parser: EventParserABC
    schema: Schema

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        self.schema.validate(event)
        parsed = self.parser.parse(event, context)
        return parsed
