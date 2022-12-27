from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema

from servey.errors import ServeyError
from servey.security.access_control.action_access_control_abc import ActionAccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class EventParser(EventParserABC):
    """
    Event parser typically used for direct lambda invocation (As opposed to api gateway / appsync)
    """
    marshaller: MarshallerABC
    schema: Optional[Schema] = None
    access_control: ActionAccessControlABC = ALLOW_ALL
    auth_param_name: Optional[str] = None  # Required if access_control != ALLOW_ALL or auth_kwarg_name present
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None
    auth_marshaller: Optional[MarshallerABC[Authorization]] = None  # Present only if direct auth is permitted

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        if self.access_control != ALLOW_ALL or self.auth_kwarg_name:
            auth_kwarg_value = event.pop(self.auth_param_name, None)
            if isinstance(auth_kwarg_value, str):
                authorization = self.authorizer.authorize(auth_kwarg_value)
            else:
                authorization = self.auth_marshaller.load(auth_kwarg_value)
            if not self.access_control.is_executable(authorization):
                raise ServeyError('access_denied')
            if self.auth_kwarg_name:
                parsed = self.marshaller.load(event)
                parsed[self.auth_kwarg_name] = authorization
                if self.schema:
                    self.schema.validate(event)
                return parsed
        parsed = self.marshaller.load(event)
        if self.schema:
            self.schema.validate(event)
        return parsed
