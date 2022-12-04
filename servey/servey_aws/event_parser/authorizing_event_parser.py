from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.types import ExternalItemType

from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import AuthorizationError
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.action.util import inject_value_at


@dataclass
class AuthorizingEventParser(EventParserABC):
    parser: EventParserABC
    authorizer: AuthorizerABC
    inject_at: Optional[str] = None
    access_control: ActionAccessControlABC = ALLOW_ALL

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        authorization = self.get_authorization(event)
        if not self.access_control.is_executable(authorization):
            raise AuthorizationError()
        parsed = self.parser.parse(event, context)
        if self.inject_at:
            inject_value_at(self.inject_at, parsed, authorization)
        return parsed

    def get_authorization(self, event: ExternalItemType):
        token = event.get("token")
        if token:
            authorization = self.authorizer.authorize(token)
            return authorization
