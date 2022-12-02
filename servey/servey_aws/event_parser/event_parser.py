from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class EventParser(EventParserABC):
    marshaller: MarshallerABC
    schema: Optional[Schema] = None

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        if self.schema:
            self.schema.validate(event)
        parsed = self.marshaller.load(event)
        return parsed
