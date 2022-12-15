from unittest import TestCase

from marshy.marshaller import DatetimeMarshaller

from servey.cache_control.cache_header import CacheHeader
from servey.cache_control.timestamp_cache_control import TimestampCacheControl


class TestTimestampCacheControl(TestCase):
    def test_get_cache_header(self):
        cache_control = TimestampCacheControl(timestamp_marshaller=DatetimeMarshaller())
        cache_header = cache_control.get_cache_header(
            dict(values=[1, "str", True], updated_at="2022-12-01 02:03:04+00:00")
        )
        expected = CacheHeader()
        self.assertIsNotNone(expected, cache_header)
