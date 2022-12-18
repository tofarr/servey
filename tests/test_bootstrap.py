from unittest import TestCase

from servey.version import __version__


class TestBootstrap(TestCase):
    def test_version(self):
        self.assertIsNotNone(__version__)
