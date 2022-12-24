import json
from dataclasses import dataclass, field
from datetime import datetime

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.cache_control.cache_control_abc import CacheControlABC
from servey.cache_control.cache_header import CacheHeader
from servey.cache_control.secure_hash_cache_control import SecureHashCacheControl


@dataclass(frozen=True)
class TimestampCacheControl(CacheControlABC):
    cache_control: CacheControlABC = SecureHashCacheControl()
    updated_at_attr: str = "updated_at"
    timestamp_marshaller: MarshallerABC[datetime] = field(
        default_factory=lambda: get_default_context().get_marshaller(datetime)
    )

    def get_cache_header(self, item: ExternalItemType):
        cache_header = self.cache_control.get_cache_header(item)
        updated_at = item.get(self.updated_at_attr)
        updated_at = self.timestamp_marshaller.load(updated_at)
        return CacheHeader(
            etag=cache_header.etag,
            updated_at=updated_at,
            expire_at=cache_header.expire_at,
            private=cache_header.private,
        )

    def get_cache_header_from_content(self, content: bytes) -> CacheHeader:
        content_json = json.loads(content)
        return self.get_cache_header(content_json)
