from abc import ABC, abstractmethod

from marshy.types import ExternalItemType

from servey.cache_control.cache_header import CacheHeader


class CacheControlABC(ABC):
    @abstractmethod
    def get_cache_header(self, item: ExternalItemType) -> CacheHeader:
        """Get the cache header for the item given"""

    @abstractmethod
    def get_cache_header_from_content(self, content: bytes) -> CacheHeader:
        """Get the cache header for the content given"""
