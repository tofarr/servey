from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from marshy.types import ExternalItemType
from schemey import schema_from_type
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.action.action import Action
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.error_response import ErrorResponse


@dataclass
class AuthorizingActionEndpoint(ActionEndpointABC):
    """
    Wrapper for a function for use within starlette, with everything needed to bind it to a route
    """

    action_endpoint: ActionEndpointABC
    authorizer: AuthorizerABC
    auth_kwarg_name: str
    error_schema: ExternalItemType = field(
        default_factory=lambda: schema_from_type(ErrorResponse).schema
    )

    def get_action(self) -> Action:
        return self.action_endpoint.get_action()

    def get_route(self) -> Route:
        route = self.action_endpoint.get_route()
        return Route(
            route.path, name=route.name, endpoint=self.execute, methods=route.methods
        )

    async def execute_with_context(
        self, request: Request, context: Dict[str, Any]
    ) -> Response:
        authorization = parse_authorization(self.authorizer, request)
        if not self.get_action().access_control.is_executable(authorization):
            return JSONResponse(dict(error="unauthorized"), 401)
        if self.auth_kwarg_name:
            context[self.auth_kwarg_name] = authorization
        response = await self.action_endpoint.execute_with_context(request, context)
        return response

    def to_openapi_schema(self, schema: ExternalItemType):
        self.action_endpoint.to_openapi_schema(schema)

        components: Dict = schema["components"]
        components["ErrorResponse"] = self.error_schema

        if not components.get("securitySchemas"):
            components["securitySchemes"] = {
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {"password": {"scopes": {}, "tokenUrl": "/login"}},
                }
            }

        route = self.action_endpoint.get_route()
        paths: Dict = schema["paths"]
        path: Dict = paths[route.path]
        for method in route.methods:
            path_method: Dict = path.get(method.lower())
            if path_method is None:
                continue
            if not path_method.get("security"):
                path_method["security"] = [{"OAuth2PasswordBearer": []}]
            responses: Dict = path_method["responses"]
            responses["403"] = {
                "description": "unauthorized",
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#components/ErrorResponse"}
                    }
                },
            }


def parse_authorization(
    authorizer: AuthorizerABC, request: Request
) -> Optional[Authorization]:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return
    token = token[7:]
    return authorizer.authorize(token)
