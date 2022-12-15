from datetime import datetime
from unittest import TestCase

from servey.cache_control.ttl_cache_control import TtlCacheControl


class TestTtlCacheControl(TestCase):
    def test_get_cache_header(self):
        cache_control = TtlCacheControl(900)
        cache_header = cache_control.get_cache_header(dict(values=[1, "str", True]))
        self.assertIsNotNone(cache_header.etag)
        self.assertAlmostEqual(
            cache_header.expire_at.timestamp(),
            datetime.now().timestamp() + 900,
            delta=1,
        )
