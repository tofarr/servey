from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from servey.cache.cache_header import CacheHeader

T = TypeVar('T')


class CacheControlABC(ABC, Generic[T]):

    @abstractmethod
    def get_cache_header(self, item: T) -> CacheHeader:
        """ Get the cache header for the item given """
