from datetime import datetime
from unittest import TestCase

from servey.cache_control.cache_header import CacheHeader


class TestCacheHeader(TestCase):
    def test_cache_control_str_no_expire(self):
        cache_header = CacheHeader("etag")
        self.assertEqual("no-storage", cache_header.get_cache_control_str())

    def test_combine_with(self):
        a = CacheHeader(
            "a",
            datetime.fromisoformat("2020-01-01"),
            datetime.fromisoformat("2020-06-01"),
        )
        b = CacheHeader(
            "b",
            datetime.fromisoformat("2020-02-01"),
            datetime.fromisoformat("2020-05-01"),
        )
        c = a.combine_with([b])
        d = b.combine_with([a])
        self.assertIsNotNone(c.etag)
        self.assertIsNotNone(d.etag)
        self.assertNotEqual(d.etag, c.etag)
        e = CacheHeader(
            c.etag,
            datetime.fromisoformat("2020-02-01"),
            datetime.fromisoformat("2020-05-01"),
        )
        self.assertEqual(e, c)
        f = CacheHeader(
            d.etag,
            datetime.fromisoformat("2020-02-01"),
            datetime.fromisoformat("2020-05-01"),
        )
        self.assertEqual(f, d)
