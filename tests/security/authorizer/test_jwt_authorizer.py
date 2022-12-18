from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.jwt_authorizer import JwtAuthorizer
from servey.security.authorizer.jwt_authorizer_factory import JwtAuthorizerFactory


class TestJwtAuthorizer(TestCase):
    def test_encode_and_authorize(self):
        authorizer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="me", aud="everybody"
        )
        authorization = _create_authorization()
        token = authorizer.encode(authorization)
        authorized = authorizer.authorize(token)
        self.assertEqual(authorized, authorization)

    def test_invalid_issuer(self):
        wrong_issuer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="wrong", aud="everybody"
        )
        no_issuer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", aud="everybody"
        )
        authorizer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="correct", aud="everybody"
        )
        authorization = _create_authorization()
        token = wrong_issuer.encode(authorization)
        with self.assertRaises(AuthorizationError):
            authorizer.authorize(token)
        token = no_issuer.encode(authorization)
        with self.assertRaises(AuthorizationError):
            authorizer.authorize(token)

    def test_invalid_audience(self):
        wrong_audience = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="me", aud="wrong"
        )
        no_audience = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="me"
        )
        authorizer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="me", aud="correct"
        )
        authorization = _create_authorization()
        token = wrong_audience.encode(authorization)
        with self.assertRaises(AuthorizationError):
            authorizer.authorize(token)
        token = no_audience.encode(authorization)
        with self.assertRaises(AuthorizationError):
            authorizer.authorize(token)

    def test_get_key_id(self):
        authorizer = JwtAuthorizer(
            private_key="SOME_SECRET_KEY", kid="mockKey", iss="me", aud="everybody"
        )
        token = authorizer.encode(
            Authorization(
                "user-1234",
                frozenset(("tinker", "tailor", "soldier", "spy")),
                None,
                None,
            )
        )
        self.assertEqual("mockKey", authorizer.get_key_id(token))

    def test_missing_module(self):
        def raise_module_not_found(_: str):
            raise ModuleNotFoundError()

        with patch(
            "servey.security.authorizer.jwt_authorizer.JwtAuthorizer",
            raise_module_not_found,
        ):
            self.assertIsNone(JwtAuthorizerFactory().create_authorizer())


def _create_authorization():
    iss = datetime.now().replace(microsecond=0)
    exp = iss + relativedelta(hours=1)
    authorization = Authorization("subjectId", frozenset(["foo", "bar"]), iss, exp)
    return authorization
