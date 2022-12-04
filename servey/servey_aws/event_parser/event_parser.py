from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema

from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class EventParser(EventParserABC):
    marshaller: MarshallerABC
    schema: Optional[Schema] = None
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None
    auth_marshaller: Optional[MarshallerABC[Authorization]] = None

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        auth_kwarg_value = None
        if self.auth_kwarg_name:
            auth_kwarg_value = event.pop(self.auth_kwarg_name, None)
        if self.schema:
            self.schema.validate(event)
        parsed = self.marshaller.load(event)
        if auth_kwarg_value:
            if isinstance(auth_kwarg_value, str):
                parsed[self.auth_kwarg_name] = self.authorizer.authorize(
                    auth_kwarg_value
                )
            elif self.auth_marshaller:
                # Given that we can invoke a lambda directly requires trust, we allow passing the authorization
                # directly. Maybe this should be revoked in favor of only having signed tokens.
                parsed[self.auth_kwarg_name] = self.auth_marshaller.load(
                    auth_kwarg_value
                )
        return parsed
