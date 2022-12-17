import base64
import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import Iterator

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from servey.security.authorization import Authorization, ROOT
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
        authenticator = RootPasswordAuthenticator()
        yield Route(path="/login", methods=["post"], endpoint=authenticator.login)


def _default_password():
    password = os.environ.get("SERVEY_DEBUG_AUTHENTICATOR_PASSWORD")
    if not password:
        password = (
            base64.b64encode(os.urandom(12))
            .decode("UTF-8")
            .replace("+", "")
            .replace("/", "")
        )
        LOGGER.warning(f"Using Temporary Password: {password}")
    return password


@dataclass
class RootPasswordAuthenticator:
    username: str = field(
        default_factory=lambda: os.environ.get("DEBUG_AUTHENTICATOR_USERNAME") or "root"
    )
    password: str = field(default_factory=_default_password)
    authorization: Authorization = field(default=ROOT)
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)

    async def login(self, request: Request) -> JSONResponse:
        form_data = await request.form()
        if (
            form_data["username"] == self.username
            and form_data["password"] == self.password
        ):
            return JSONResponse(
                {
                    "access_token": self.authorizer.encode(self.authorization),
                    "token_type": "bearer",
                }
            )
        raise HTTPException(status_code=400, detail="Incorrect username or password")
