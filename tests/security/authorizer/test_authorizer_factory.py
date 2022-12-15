from unittest import TestCase

from servey.security.authorizer.authorizer_factory_abc import (
    create_authorizer,
    get_default_authorizer,
)
from servey.security.authorizer.jwt_authorizer import JwtAuthorizer


class TestAuthorizerFactory(TestCase):
    def test_create_authorizer(self):
        authorizer1 = create_authorizer()
        self.assertIsInstance(authorizer1, JwtAuthorizer)
        authorizer2 = create_authorizer()
        self.assertIsInstance(authorizer2, JwtAuthorizer)
        self.assertNotEqual(authorizer1.private_key, authorizer2.private_key)

    def test_get_default_authorizer(self):
        self.assertIs(get_default_authorizer(), get_default_authorizer())
