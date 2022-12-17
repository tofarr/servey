from enum import Enum, EnumMeta
from unittest import TestCase

from servey.servey_strawberry.entity_factory.enum_factory import EnumFactory
from servey.servey_strawberry.schema_factory import SchemaFactory


class TestEnumFactory(TestCase):
    def test_create_input(self):
        input_ = EnumFactory().create_input(_FooBar, SchemaFactory())
        self.assertIs(EnumMeta, input_.__class__)
        # noinspection PyTypeChecker
        self.assertEqual(["foo", "bar"], [e.value for e in input_])


class _FooBar(Enum):
    FOO = "foo"
    BAR = "bar"
