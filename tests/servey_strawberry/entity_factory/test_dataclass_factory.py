from unittest import TestCase

from dateutil.relativedelta import relativedelta

# noinspection PyProtectedMember
from servey.servey_strawberry.entity_factory.dataclass_factory import _UserCache


class TestDataclassFactory(TestCase):
    def test_user_cache(self):
        cache = _UserCache(relativedelta(seconds=10))
        cache.set("foo", "bar")
        self.assertEqual(cache.get("foo"), "bar")
        cache.delete("foo")
        self.assertIsNone(cache.get("foo"))
        cache.set("foo", "bar")
        cache.clear()
        self.assertIsNone(cache.get("foo"))
