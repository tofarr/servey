import json
from dataclasses import dataclass
from typing import Dict, Any, Optional

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC


@dataclass
class ApiGatewayEventParser(EventParserABC):
    marshaller: MarshallerABC
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None

    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        if event.get("httpMethod") in ("POST", "PATCH", "PUT"):
            params = json.loads(event.get("body") or "{}")
        else:
            params = event.get("queryStringParameters") or {}
        parsed = self.marshaller.load(params)
        if self.auth_kwarg_name:
            parsed[self.auth_kwarg_name] = self.get_authorization(event)
        return parsed

    def get_authorization(self, event: ExternalItemType) -> Optional[Authorization]:
        headers = event.get("headers") or {}
        token = (headers.get("Authorization") or "").strip()
        if not token or not token.startswith("Bearer "):
            return
        token = token[7:]
        return self.authorizer.authorize(token)
