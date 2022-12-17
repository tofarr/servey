from unittest import TestCase

from servey.cache_control.cache_header import CacheHeader
from servey.cache_control.secure_hash_cache_control import SecureHashCacheControl


class TestSecureHashCacheControl(TestCase):
    def test_get_cache_header(self):
        cache_control = SecureHashCacheControl()
        cache_header = cache_control.get_cache_header(dict(values=[1, "str", True]))
        # noinspection SpellCheckingInspection
        expected = CacheHeader("IjLwXxgJicusWH98zrk+2VzPUZ+FuDMknuo3fdOzIEs=")
        self.assertEqual(expected, cache_header)

    def test_get_cache_header_public(self):
        cache_control = SecureHashCacheControl(private=False)
        cache_header = cache_control.get_cache_header(dict(values=[2, "str", True]))
        # noinspection SpellCheckingInspection
        expected = CacheHeader(
            "HxYzJNnJVRCdsnux0p3vdUajMtJFiZY1FFKXsF0RUPc=", private=False
        )
        self.assertEqual(expected, cache_header)
