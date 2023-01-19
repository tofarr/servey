import os

from dataclasses import dataclass, field
from logging import getLogger
from typing import Iterator

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from servey.security.authenticator.password_authenticator_abc import (
    PasswordAuthenticatorABC,
    get_default_password_authenticator,
)
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

LOGGER = getLogger(__name__)


class AuthenticatorRouteFactory(RouteFactoryABC):
    """Route factory which performs authentication."""

    def create_routes(self) -> Iterator[Route]:
        # Create an authenticator object based on username and password
        if os.environ.get("SERVEY_DEBUG_AUTHENTICATOR") == "0":
            return
        authenticator = PasswordLoginEndpoint()
        yield Route(path="/login", methods=["post"], endpoint=authenticator.login)


@dataclass
class PasswordLoginEndpoint:
    password_authenticator: PasswordAuthenticatorABC = field(
        default_factory=get_default_password_authenticator
    )
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)

    async def login(self, request: Request) -> JSONResponse:
        form_data = await request.form()
        authorization = self.password_authenticator.authenticate(
            form_data["username"], form_data["password"]
        )
        if authorization:
            return JSONResponse(
                {
                    "access_token": self.authorizer.encode(authorization),
                    "token_type": "bearer",
                }
            )
        raise HTTPException(status_code=400, detail="Incorrect username or password")
