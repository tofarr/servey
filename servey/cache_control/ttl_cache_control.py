from dataclasses import dataclass
from datetime import datetime
from time import time

from marshy.types import ExternalItemType

from servey.cache_control.cache_control_abc import CacheControlABC
from servey.cache_control.cache_header import CacheHeader
from servey.cache_control.secure_hash_cache_control import SecureHashCacheControl


@dataclass(frozen=True)
class TtlCacheControl(CacheControlABC):
    ttl: int
    cache_control: CacheControlABC = SecureHashCacheControl()

    def get_cache_header(self, item: ExternalItemType):
        cache_header = self.cache_control.get_cache_header(item)
        return self._wrap_cache_header(cache_header)

    def get_cache_header_from_content(self, content: bytes) -> CacheHeader:
        cache_header = self.cache_control.get_cache_header_from_content(content)
        return self._wrap_cache_header(cache_header)

    def _wrap_cache_header(self, cache_header: CacheHeader):
        expire_at = datetime.fromtimestamp(int(time()) + self.ttl)
        return CacheHeader(
            etag=cache_header.etag,
            updated_at=cache_header.updated_at,
            expire_at=expire_at,
            private=cache_header.private,
        )
