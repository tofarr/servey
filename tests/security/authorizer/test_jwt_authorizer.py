from datetime import datetime
from unittest import TestCase

from dateutil.relativedelta import relativedelta

from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.jwt_authorizer import JwtAuthorizer


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


def _create_authorization():
    iss = datetime.now().replace(microsecond=0)
    exp = iss + relativedelta(hours=1)
    authorization = Authorization("subjectId", frozenset(["foo", "bar"]), iss, exp)
    return authorization
