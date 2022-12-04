from dataclasses import dataclass
from typing import Dict, Any

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class AppsyncEventParser(EventParserABC):
    marshaller: MarshallerABC

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        arguments = event["arguments"] or {}
        parsed = self.marshaller.load(arguments)
        # TODO: Pass in an authentication header here?
        return parsed
