from unittest import TestCase

from servey.security.access_control.allow_none import ALLOW_NONE, AllowNone
from servey.security.authorization import ROOT


class TestAllowAll(TestCase):
    def test_singleton(self):
        self.assertIs(ALLOW_NONE, AllowNone())

    def test_methods(self):
        self.assertFalse(ALLOW_NONE.is_executable(ROOT))
