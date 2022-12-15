from dataclasses import dataclass

from marshy.types import ExternalItemType

from servey.cache_control.cache_control_abc import CacheControlABC
from servey.cache_control.cache_header import CacheHeader
from servey.util import secure_hash, secure_hash_content


@dataclass(frozen=True)
class SecureHashCacheControl(CacheControlABC):
    private: bool = True

    def get_cache_header(self, item: ExternalItemType) -> CacheHeader:
        etag = secure_hash(item)
        return CacheHeader(etag=etag, private=self.private)

    def get_cache_header_from_content(self, content: bytes) -> CacheHeader:
        etag = secure_hash_content(content)
        return CacheHeader(etag=etag, private=self.private)
