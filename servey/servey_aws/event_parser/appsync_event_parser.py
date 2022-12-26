from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class AppsyncEventParser(EventParserABC):
    marshaller: MarshallerABC
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        info: Dict = event["info"]
        variables = info["variables"]
        parsed = self.marshaller.load(variables)
        return parsed
