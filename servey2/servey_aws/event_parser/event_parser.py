from dataclasses import dataclass
from typing import Dict, Any

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey2.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class EventParser(EventParserABC):
    marshaller: MarshallerABC

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        parsed = self.marshaller.load(event)
        return parsed
