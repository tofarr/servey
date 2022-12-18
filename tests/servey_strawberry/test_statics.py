from unittest import TestCase

from servey.servey_strawberry import statics


class TestBootstrap(TestCase):
    def test_exists(self):
        self.assertIsNotNone(statics)
