from dataclasses import dataclass
from typing import Optional, Dict, Any

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import AuthorizationError
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC
from servey.action.util import inject_value_at


@dataclass
class AuthorizingParser(RequestParserABC):
    """
    Parser which pulls kwargs from a request body
    """

    authorizer: AuthorizerABC
    parser: RequestParserABC
    inject_at: Optional[str] = None
    access_control: ActionAccessControlABC = ALLOW_ALL

    async def parse(self, request: Request) -> Dict[str, Any]:
        authorization = self.get_authorization(request)
        if not self.access_control.is_executable(authorization):
            raise AuthorizationError()
        kwargs = await self.parser.parse(request)
        if self.inject_at:
            inject_value_at(self.inject_at, kwargs, authorization)
        return kwargs

    def get_authorization(self, request: Request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return
        token = token[7:]
        return self.authorizer.authorize(token)

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        responses: ExternalItemType = path_method["responses"]
        if not responses.get("403"):
            responses["403"] = {"description": "Unauthorized"}
        if not path_method.get("security"):
            path_method["security"] = [{"OAuth2PasswordBearer": []}]
        if not components.get("securitySchemas"):
            components["securitySchemes"] = {
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {"password": {"scopes": {}, "tokenUrl": "/login"}},
                }
            }
