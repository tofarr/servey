import json
from dataclasses import dataclass
from typing import Dict, Any

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class ApiGatewayEventParser(EventParserABC):
    marshaller: MarshallerABC

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        if event.get('httpMethod') in ('POST', 'PATCH', 'PUT'):
            params = json.loads(event.get('body') or '{}')
        else:
            params = event.get('queryStringParameters') or {}
        # TODO: Pass in an authentication header here?
        parsed = self.marshaller.load(params)
        return parsed
