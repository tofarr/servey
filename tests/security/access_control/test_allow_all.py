from unittest import TestCase

from servey.security.access_control.allow_all import AllowAll, ALLOW_ALL
from servey.security.authorization import Authorization, PUBLIC


class TestAllowAll(TestCase):
    def test_singleton(self):
        self.assertIs(ALLOW_ALL, AllowAll())

    def test_methods(self):
        self.assertTrue(
            ALLOW_ALL.is_viewable(Authorization(None, frozenset(), None, None))
        )
        self.assertTrue(ALLOW_ALL.is_executable(PUBLIC))
