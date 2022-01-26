from dataclasses import dataclass

from servey.cache.cache_control_abc import CacheControlABC, T
from servey.cache.cache_header import CacheHeader

NO_CACHE_HEADER = CacheHeader()


@dataclass
class NoCacheControl(CacheControlABC):
    """
    Cache control that does not cache anything
    """

    def get_cache_header(self, item: T) -> CacheHeader:
        return NO_CACHE_HEADER
