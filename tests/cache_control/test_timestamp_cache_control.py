from unittest import TestCase

from marshy.marshaller import DatetimeMarshaller

from servey.cache_control.cache_header import CacheHeader
from servey.cache_control.timestamp_cache_control import TimestampCacheControl


class TestTimestampCacheControl(TestCase):
    def test_get_cache_header(self):
        cache_control = TimestampCacheControl(timestamp_marshaller=DatetimeMarshaller())
        cache_header = cache_control.get_cache_header_from_content(
            '{"values": [1, "str", true], "updated_at": "2022-12-01 02:03:04+00:00"}'.encode()
        )
        expected = CacheHeader()
        self.assertIsNotNone(expected, cache_header)
