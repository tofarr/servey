import asyncio
import os
from unittest import TestCase
from unittest.mock import patch

from starlette.exceptions import HTTPException

from servey.security.authenticator.root_password_authenticator import (
    RootPasswordAuthenticator,
)
from servey.servey_starlette.route_factory.authenticator_route_factory import (
    AuthenticatorRouteFactory,
    PasswordLoginEndpoint,
)
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestAuthenticatorRouteFactory(TestCase):
    def test_environment_variable(self):
        with patch.dict(os.environ, {"SERVEY_DEBUG_AUTHENTICATOR": "0"}):
            self.assertEqual([], list(AuthenticatorRouteFactory().create_routes()))

    def test_root_password_authenticator(self):
        authenticator = PasswordLoginEndpoint(
            RootPasswordAuthenticator("admin", "Password123!")
        )
        request = build_request(
            method="POST",
            body="username=admin&password=Password123!",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(authenticator.login(request))
        self.assertEqual(200, response.status_code)

    def test_root_password_authenticator_wrong_password(self):
        authenticator = PasswordLoginEndpoint(
            RootPasswordAuthenticator("admin", "Password123!")
        )
        request = build_request(
            method="POST",
            body="username=admin&password=NotCorrect",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        with self.assertRaises(HTTPException):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(authenticator.login(request))
