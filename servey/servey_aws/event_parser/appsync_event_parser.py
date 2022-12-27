from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema

from servey.security.access_control.action_access_control_abc import ActionAccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class AppsyncEventParser(EventParserABC):
    """
    Event parser for events from appsync. We use appsyncs built in caching
    """
    marshaller: MarshallerABC
    schema: Optional[Schema] = None  # We still need this because appsync does not validate everything
    access_control: ActionAccessControlABC = ALLOW_ALL
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        info: Dict = event["info"]
        variables = info["variables"]
        parsed = self.marshaller.load(variables)
        return parsed
