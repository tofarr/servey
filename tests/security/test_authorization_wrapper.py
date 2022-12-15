import inspect
from unittest import TestCase

from servey.security.authorization import Authorization, ROOT
from servey.security.authorization_wrapper import get_inject_at, AuthorizationWrapper


class TestAuthorizationWrapper(TestCase):
    def test_wrapper(self):
        kwarg = get_inject_at(my_fn)
        authorization_wrapper = AuthorizationWrapper(my_fn, kwarg, ROOT)
        sig = inspect.signature(authorization_wrapper.__call__)
        self.assertEqual(1, len(sig.parameters))
        result = authorization_wrapper("Testy")
        expected = "Your name is Testy and your scopes are root"
        self.assertEqual(expected, result)


def my_fn(name: str, authorization: Authorization) -> str:
    return f"Your name is {name} and your scopes are {', '.join(authorization.scopes)}"
